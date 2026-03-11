from dataclasses import dataclass, field


@dataclass
class Claim:
    """A single claim — a key-value pair describing a user attribute."""

    type: str
    value: str


@dataclass
class ClaimsPrincipal:
    """
    Represents the authenticated user's identity and associated claims.
    Inspired by .NET's ClaimsPrincipal.
    """

    user_id: str
    email: str
    claims: list[Claim] = field(default_factory=list)

    def has_claim(self, claim_type: str, claim_value: str | None = None) -> bool:
        """Check if the principal has a specific claim."""
        for claim in self.claims:
            if claim.type == claim_type:
                if claim_value is None or claim.value == claim_value:
                    return True
        return False

    def find_first(self, claim_type: str) -> Claim | None:
        """Return the first claim matching the given type."""
        for claim in self.claims:
            if claim.type == claim_type:
                return claim
        return None

    @property
    def roles(self) -> list[str]:
        """Convenience: extract all role claims."""
        return [c.value for c in self.claims if c.type == "role"]
