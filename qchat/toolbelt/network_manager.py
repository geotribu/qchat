#! python3  # noqa: E265

"""
Perform network request.
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import logging
from functools import lru_cache
from typing import Optional
from urllib.parse import urlparse, urlunparse

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QByteArray, QCoreApplication, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from qchat.__about__ import __title__, __version__
from qchat.toolbelt.log_handler import PlgLogger
from qchat.toolbelt.preferences import PlgOptionsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


class NetworkRequestsManager:
    """Helper on network operations.

    :param tr: method to translate
    :type tr: func
    """

    def __init__(self):
        """Initialization."""
        self.log = PlgLogger().log
        self.ntwk_requester = QgsBlockingNetworkRequest()

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    @lru_cache(maxsize=128)
    def add_utm_to_url(self, url: str) -> str:
        """Returns the URL using the plugin settings.

        :param url: input URL to complete
        :type url: str

        :return: Qt URL object with full parameters
        :rtype: QUrl
        """
        parsed_url = urlparse(url)
        clean_url = parsed_url._replace(
            query=PlgOptionsManager.get_plg_settings().request_path
        )
        return urlunparse(clean_url)

    @lru_cache(maxsize=128)
    def build_url(self, url: str) -> QUrl:
        """Returns the URL using the plugin settings.

        :param url: input URL to complete
        :type url: str

        :return: Qt URL object with full parameters
        :rtype: QUrl
        """
        return QUrl(self.add_utm_to_url(url))

    def build_request(self, url: Optional[QUrl] = None) -> QNetworkRequest:
        """Build request object using plugin settings.

        :return: network request object.
        :rtype: QNetworkRequest
        """
        # if URL is not specified, let's use the default one
        if not url:
            url = self.build_url()

        # create network object
        qreq = QNetworkRequest(url=url)

        # headers
        headers = {
            b"Accept": bytes(self.plg_settings.http_content_type, "utf8"),
            b"User-Agent": bytes(self.plg_settings.http_user_agent, "utf8"),
        }
        for k, v in headers.items():
            qreq.setRawHeader(k, v)

        return qreq

    def get_from_source(
        self,
        url: Optional[str] = None,
        headers: Optional[dict] = None,
        response_expected_content_type: str = "application/xml",
        use_cache: bool = True,
    ) -> Optional[QByteArray]:
        """Method to retrieve a RSS feed from a referenced source in preferences. \
        Can use cache if wanted, or not.

        :raises ConnectionError: if any problem occurs during feed fetching.
        :raises TypeError: if response mime-type is not valid

        :return: feed response in bytes
        :rtype: QByteArray

        :example:

        .. code-block:: python

            import json
            response_as_dict = json.loads(str(response, "UTF8"))
        """
        if not url:
            url = self.build_url(PlgOptionsManager.get_plg_settings().rss_source)
        else:
            url = self.build_url(url)

        try:
            # prepare request
            req = QNetworkRequest(QUrl(url))
            if headers:
                for k, v in headers.items():
                    req.setRawHeader(k, v)
            else:
                req.setHeader(
                    QNetworkRequest.KnownHeaders.UserAgentHeader,
                    bytes(f"{__title__}/{__version__}", "utf8"),
                )

            req_status = self.ntwk_requester.get(
                request=req,
                forceRefresh=not use_cache,
            )

            # check if request is fine
            if req_status != QgsBlockingNetworkRequest.ErrorCode.NoError:
                self.log(
                    message=self.ntwk_requester.errorMessage(), log_level=2, push=1
                )
                raise ConnectionError(self.ntwk_requester.errorMessage())

            self.log(
                message=f"Request to {url} succeeded.",
                log_level=3,
                push=False,
            )

            req_reply = self.ntwk_requester.reply()
            if req_reply.rawHeader(b"Content-Type") != response_expected_content_type:
                raise TypeError(
                    f"Response mime-type is '{req_reply.rawHeader(b'Content-type')}' "
                    f"not '{response_expected_content_type}' as required.".format()
                )

            return req_reply.content()

        except Exception as err:
            err_msg = f"Houston, we've got a problem: {err}"
            logger.error(err_msg)
            self.log(message=err_msg, log_level=2, push=True)
