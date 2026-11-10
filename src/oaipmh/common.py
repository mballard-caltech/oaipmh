from __future__ import annotations

from importlib.metadata import version as _get_version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import datetime as dt

    from lxml import etree


class Header:
    def __init__(
        self,
        element: etree._Element | None,
        identifier,
        datestamp: dt.datetime,
        setspec: list[str],
        deleted: bool,
    ):
        self._element = element
        # force identifier to be a string, it might be
        # an lxml.etree._ElementStringResult...
        self._identifier: str = str(identifier)
        self._datestamp: dt.datetime = datestamp
        self._setspec: list[str] = setspec
        self._deleted: bool = deleted

    def element(self) -> etree._Element | None:
        return self._element

    def identifier(self) -> str:
        return self._identifier

    def datestamp(self) -> dt.datetime:
        return self._datestamp

    def setSpec(self) -> list[str]:
        return self._setspec

    def isDeleted(self) -> bool:
        return self._deleted


class Metadata:
    def __init__(self, element: etree._Element, map: dict):
        self._element: etree._Element = element
        self._map: dict = map

    def element(self) -> etree._Element:
        return self._element

    def getMap(self) -> dict:
        return self._map

    def getField(self, name):
        return self._map[name]

    __getitem__ = getField


class Identify:
    def __init__(
        self,
        repositoryName: str,
        baseURL: str,
        protocolVersion: str,
        adminEmails: list[str],
        earliestDatestamp: dt.datetime,
        deletedRecord: str,
        granularity: str,
        compression: list[str],
        toolkit_description: bool = True,
    ):
        self._repositoryName: str = repositoryName
        self._baseURL: str = baseURL
        self._protocolVersion: str = protocolVersion
        self._adminEmails: list[str] = adminEmails
        self._earliestDatestamp: dt.datetime = earliestDatestamp
        self._deletedRecord: str = deletedRecord
        self._granularity: str = granularity
        self._compression: list[str] = compression
        self._descriptions: list[str] = []

        if toolkit_description:
            try:
                version = "<version>{}</version>".format(_get_version("oaipmh"))
            except Exception:
                version = ""
            self.add_description(
                "<toolkit xsi:schemaLocation="
                '"http://oai.dlib.vt.edu/OAI/metadata/toolkit '
                'http://oai.dlib.vt.edu/OAI/metadata/toolkit.xsd" '
                'xmlns="http://oai.dlib.vt.edu/OAI/metadata/toolkit" '
                'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                "<title>oaipmh</title>"
                f"{version}"
                "<URL>https://github.com/eth-library/oaipmh</URL>"
                "</toolkit>"
            )

    def repositoryName(self) -> str:
        return self._repositoryName

    def baseURL(self) -> str:
        return self._baseURL

    def protocolVersion(self) -> str:
        return self._protocolVersion

    def adminEmails(self) -> list[str]:
        return self._adminEmails

    def earliestDatestamp(self) -> dt.datetime:
        return self._earliestDatestamp

    def deletedRecord(self) -> str:
        return self._deletedRecord

    def granularity(self) -> str:
        return self._granularity

    def compression(self) -> list[str]:
        return self._compression

    def add_description(self, xml_string) -> None:
        self._descriptions.append(xml_string)

    def descriptions(self) -> list[str]:
        return self._descriptions


def ResumptionTokenSpec(dict):
    dict = dict.copy()
    dict["resumptionToken"] = "exclusive"
    return dict


class OAIMethodImpl:
    def __init__(self, verb):
        self._verb = verb

    def __call__(self, bound_self, **kw):
        return bound_self.handleVerb(self._verb, kw)


def OAIMethod(verb):
    obj = OAIMethodImpl(verb)

    def method(self, **kw):
        return obj(self, **kw)

    return method


class OAIPMH:
    """Mixin that implements the Python-level OAI-PMH interface.

    It does not include resumptionToken handling.

    It passes the calls on to the 'handleVerb' method, which should be
    overridden in a subclass.
    """

    def handleVerb(self, verb, kw):
        raise NotImplementedError

    getRecord = OAIMethod(
        "GetRecord",
    )

    getMetadata = OAIMethod(
        "GetMetadata",
    )

    identify = OAIMethod(
        "Identify",
    )

    listIdentifiers = OAIMethod(
        "ListIdentifiers",
    )

    listMetadataFormats = OAIMethod(
        "ListMetadataFormats",
    )

    listRecords = OAIMethod(
        "ListRecords",
    )

    listSets = OAIMethod(
        "ListSets",
    )


class ResumptionOAIPMH:
    """Mixin that implements the Resumption-capable OAI-PMH interface.

    It passes the arguments on to the 'handleVerb' method, which
    should be overridden in a subclass.

    The listIdentifiers, listSets and listRecords methods return
    tuples of a list and resumptionToken. If the resumptionToken
    returned is None, this indicates the end of the list is reached.
    """

    def handleVerb(self, verb, kw):
        raise NotImplementedError

    getRecord = OAIMethod(
        "GetRecord",
    )

    getMetadata = OAIMethod(
        "GetMetadata",
    )

    identify = OAIMethod(
        "Identify",
    )

    listIdentifiers = OAIMethod(
        "ListIdentifiers",
    )

    listMetadataFormats = OAIMethod(
        "ListMetadataFormats",
    )

    listRecords = OAIMethod(
        "ListRecords",
    )

    listSets = OAIMethod(
        "ListSets",
    )


def getMethodForVerb(server, verb):
    return getattr(server, verb[0].lower() + verb[1:])
