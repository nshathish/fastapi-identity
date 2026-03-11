from dataclasses import dataclass, field


@dataclass
class Claim:
    type: str
    value: str


@dataclass
class ClaimsPrincipal:
    user_id: str
    email: str
    claims: list[Claim] = field(default_factory=list)

    def has_claim(self, claim_type: str, claim_value: str | None = None) -> bool:
        for claim in self.claims:
            if claim.type == claim_type:
                if claim_value is None or claim.value == claim_value:
                    return True
        return False

    def find_first(self, claim_type: str) -> Claim | None:
        for claim in self.claims:
            if claim.type == claim_type:
                return claim
        return None

    @property
    def roles(self) -> list[str]:
        return [c.value for c in self.claims if c.type == "role"]
