"""Build the immutable evidence for one running archive."""

from dataclasses import dataclass
from hashlib import sha256
from secrets import token_hex
from types import MappingProxyType
from typing import Mapping


MESSAGE = "message.txt"
AUDIT = "audit.log"
CREDENTIAL = "records/vault-passphrase.txt"
CURRENT = "04"


@dataclass(frozen=True)
class Revision:
    number: str
    title: str
    description: str
    files: Mapping[str, bytes]

    def summary(self):
        return {
            "id": self.number,
            "title": self.title,
            "description": self.description,
            "current": self.number == CURRENT,
        }

    def listing(self):
        return {**self.summary(), "files": list(self.files)}


@dataclass(frozen=True, repr=False)
class Evidence:
    case_reference: str
    certified_digest: bytes
    recovery_phrase: bytes
    revisions: Mapping[str, Revision]


def generate_evidence():
    case_reference = f"KRA-{token_hex(5).upper()}"
    recovery_phrase = f"OWL-{token_hex(7).upper()}".encode("ascii")

    original = (
        "KEEPER'S RECOVERY NOTE\n"
        f"Case reference: {case_reference}\n"
        "\n"
        "Retain this note for reinstatement of the Keeper's Vault.\n"
        "Present the certified copy with the archive recovery phrase.\n"
        f"Archived phrase location: {CREDENTIAL}\n"
    ).encode("utf-8")
    current = original[:-1]
    digest = sha256(original)
    audit = (
        "INTEGRITY CERTIFICATION LEDGER\n"
        f"Case reference: {case_reference}\n"
        f"Certified filename: {MESSAGE}\n"
        "Algorithm: SHA-256\n"
        f"Certified digest: {digest.hexdigest()}\n"
        "\n"
        "The archivist certified the recovery note held in this revision.\n"
    ).encode("utf-8")
    credential = f"Case reference: {case_reference}\nRecovery phrase: ".encode("ascii")
    credential += recovery_phrase + b"\n"

    revisions = (
        Revision("01", "Initial Archive Registration",
                 "Initial recovery documents registered in the archive.",
                 MappingProxyType({MESSAGE: original, CREDENTIAL: credential})),
        Revision("02", "Access Record Retired",
                 "An obsolete access record was removed during routine maintenance.",
                 MappingProxyType({MESSAGE: original})),
        Revision("03", "Integrity Certification",
                 "Archivist integrity certification entered into the ledger.",
                 MappingProxyType({MESSAGE: original, AUDIT: audit})),
        Revision(CURRENT, "Formatting Maintenance",
                 "Minor formatting cleanup applied to recovery documentation.",
                 MappingProxyType({MESSAGE: current, AUDIT: audit})),
    )
    return Evidence(case_reference, digest.digest(), recovery_phrase,
                    MappingProxyType({revision.number: revision for revision in revisions}))
