from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import Iterable

    from oaipmh.common import Metadata

    Record = tuple["IHeader", Metadata | None, Any]


class IOAI(Protocol):
    def getRecord(self, metadataPrefix: str, identifier: str) -> Record:
        """Get a record for a metadataPrefix and identifier.

        metadataPrefix - identifies metadata set to retrieve
        identifier - repository-unique identifier of record

        Should raise error.CannotDisseminateFormatError if
        metadataPrefix is unknown or not supported by identifier.

        Should raise error.IdDoesNotExistError if identifier is
        unknown or illegal.

        Returns a header, metadata, about tuple describing the record.
        """
        ...

    def identify(self) -> IIdentify:
        """Retrieve information about the repository.

        Returns an Identify object describing the repository.
        """
        ...

    def listIdentifiers(
        self,
        metadataPrefix: str,
        set: str | None = None,
        from_: dt.datetime | None = None,
        until: dt.datetime | None = None,
    ) -> Iterable[IHeader]:
        """Get a list of header information on records.

        metadataPrefix - identifies metadata set to retrieve
        set - set identifier; only return headers in set (optional)
        from_ - only retrieve headers from from_ date forward (optional)
        until - only retrieve headers with dates up to and including
                until date (optional)

        Should raise error.CannotDisseminateFormatError if metadataPrefix
        is not supported by the repository.

        Should raise error.NoSetHierarchyError if the repository does not
        support sets.

        Returns an iterable of headers.
        """

    def listMetadataFormats(
        self, identifier: str | None = None
    ) -> Iterable[tuple[str, str, str]]:
        """List metadata formats supported by repository or record.

        identifier - identify record for which we want to know all
                     supported metadata formats. if absent, list all metadata
                     formats supported by repository. (optional)


        Should raise error.IdDoesNotExistError if record with
        identifier does not exist.

        Should raise error.NoMetadataFormatsError if no formats are
        available for the indicated record.

        Returns an iterable of metadataPrefix, schema, metadataNamespace
        tuples (each entry in the tuple is a string).
        """

    def listRecords(
        self,
        metadataPrefix: str,
        set: str | None = None,
        from_: dt.datetime | None = None,
        until: dt.datetime | None = None,
    ) -> Iterable[Record]:
        """Get a list of header, metadata and about information on records.

        metadataPrefix - identifies metadata set to retrieve
        set - set identifier; only return records in set (optional)
        from_ - only retrieve records from from_ date forward (optional)
        until - only retrieve records with dates up to and including
                until date (optional)

        Should raise error.CannotDisseminateFormatError if metadataPrefix
        is not supported by the repository.

        Should raise error.NoSetHierarchyError if the repository does not
        support sets.

        Returns an iterable of header, metadata, about tuples.
        """

    def listSets(self) -> Iterable[tuple[str, str, str | None]]:
        """Get a list of sets in the repository.

        Should raise error.NoSetHierarchyError if the repository does not
        support sets.

        Returns an iterable list of tuples(setSpec, setName, setDescription).
        setSpec and setName are strings. setDescription is a string or None.
        """


class IBatchingOAI(Protocol):
    """Very similar to IOAI, but the implementation can be batch-aware.

    Methods that support resumption will get two extra arguments,
    cursor and batch_size, which indicate the batch currently being
    requested.
    """

    def getRecord(self, metadataPrefix: str, identifier: str) -> Record: ...

    def identify(self) -> IIdentify: ...

    def listIdentifiers(
        self,
        metadataPrefix: str,
        set: str | None = None,
        from_: dt.datetime | None = None,
        until: dt.datetime | None = None,
        cursor: int = 0,
        batch_size: int = 10,
    ) -> Iterable[IHeader]: ...

    def listMetadataFormats(
        self, identifier: str | None = None
    ) -> Iterable[tuple[str, str, str]]: ...

    def listRecords(
        self,
        metadataPrefix: str,
        set: str | None = None,
        from_: dt.datetime | None = None,
        until: dt.datetime | None = None,
        cursor: int = 0,
        batch_size: int = 10,
    ) -> Iterable[Record]: ...

    def listSets(
        self, cursor: int = 0, batch_size: int = 10
    ) -> Iterable[tuple[str, str, str | None]]: ...


class IResumptionOAI(Protocol):
    """An interface for OAI servers that accept a resumptionToken.

    For all functions that can take a resumptionToken:
        - if it is passed then all other arguments must be None.
        - if that token is invalid then the fns raise badResumptionToken.
    """

    def getRecord(self, metadataPrefix: str, identifier: str) -> Record: ...

    def identify(self) -> IIdentify: ...

    def listIdentifiers(
        self,
        metadataPrefix: str | None = None,
        set: str | None = None,
        from_: dt.datetime | None = None,
        until: dt.datetime | None = None,
        resumptionToken: str | None = None,
    ) -> tuple[Iterable[IHeader], str | None]: ...

    def listMetadataFormats(
        self, identifier: str | None = None
    ) -> Iterable[tuple[str, str, str]]: ...

    def listRecords(
        self,
        metadataPrefix: str | None = None,
        set: str | None = None,
        from_: dt.datetime | None = None,
        until: dt.datetime | None = None,
        resumptionToken: str | None = None,
    ) -> tuple[Iterable[Record], str | None]: ...

    def listSets(
        self,
        resumptionToken: str | None = None,
    ) -> tuple[Iterable[tuple[str, str, str | None]], str | None]: ...


class IIdentify(Protocol):
    def repositoryName(self) -> str:
        """Name of repository."""
        ...

    def baseURL(self) -> str:
        """Base URL for OAI-PMH requests."""
        ...

    def protocolVersion(self) -> str:
        """OAI-PMH protocol version (should always be '2.0')"""
        ...

    def adminEmails(self) -> list[str]:
        """List of email addresses of repository administrators."""
        ...

    def earliestDatestamp(self) -> dt.datetime:
        """The datetime (datestamp) of the earliest record in repository."""
        ...

    def deletedRecord(self) -> str:
        """Way the repository handles deleted records.

        Either 'no', 'transient' or 'persistent'.
        """
        ...

    def granularity(self) -> str:
        """Datetime granularity of datestamps in repository.

        Either YYYY-MM-DD or YYYY-MM-DDThh:mm:ssZ
        """
        ...

    def compression(self) -> list[str]:
        """List of types of compression schemes supported by repository.

        'identity' is the 'do-nothing' scheme.
        """
        ...

    def descriptions(self) -> Iterable[str]:
        """a list of xml strings that are descriptions of the service."""
        ...


class IHeader(Protocol):
    def identifier(self) -> str:
        """Repository-unique identifier of this record."""
        ...

    def datestamp(self) -> dt.datetime:
        """Datetime of creation, last modification or deletion of the record.

        This can be used for selective harvesting.
        """
        ...

    def setSpec(self) -> list[str]:
        """A list of sets this record is a member of."""
        ...

    def isDeleted(self) -> bool:
        """If true, record has been deleted."""
        ...
