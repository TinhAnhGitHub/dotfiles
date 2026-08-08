# pydantic-extra-types

Use this reference when a model needs a domain-format type that is not in the
Pydantic core package. Inspect the installed version and optional dependency
extras first; the rolling API index can lag behind package modules.

## Installation and boundary

```bash
pip install pydantic-extra-types
pip install 'pydantic-extra-types[phonenumbers,pycountry,semver]'
```

The package is separate from `pydantic`. It integrates through Pydantic v2 schemas,
but its optional dependencies and available exports are version-sensitive. Do not
assume that a type imported from an old v1 path still exists in `pydantic`.

## API catalog

| Module | Representative exports | Typical use |
|---|---|---|
| `color` | `Color` | CSS colors and conversion helpers |
| `coordinate` | `Latitude`, `Longitude`, `Coordinate` | bounded geographic coordinates |
| `country` | `CountryAlpha2`, `CountryAlpha3`, `CountryNumericCode` | ISO 3166 codes |
| `currency_code` | `ISO4217`, `Currency` | currency codes |
| `isbn` | `ISBN` | ISBN-10/13 validation/normalization |
| `language_code` | `LanguageAlpha2`, `LanguageName`, `ISO639_3` | language codes |
| `mac_address` | `MacAddress` | MAC/EUI addresses |
| `payment` | `PaymentCardNumber`, `PaymentCardBrand` | card format/checksum validation |
| `pendulum_dt` | `DateTime`, `Date`, `Time`, `Duration` | Pendulum values (extra required) |
| `phone_numbers` | `PhoneNumber`, `PhoneNumberValidator` | libphonenumber parsing (extra required) |
| `routing_number` | `ABARoutingNumber` | ABA checksum format |
| `script_code` | `ISO_15924` | ISO 15924 script codes |
| `semantic_version` | `SemanticVersion` | SemVer values (extra required) |
| `timezone_name` | `TimeZoneName` | IANA time-zone names |
| `ulid` | `ULID` | sortable ULIDs (extra required) |
| — | UUID1–UUID8 | These are current `pydantic.types` aliases, not an extra-types module; verify the installed package before assuming an extra dependency |

The canonical API pages are listed in
<https://pydantic.dev/docs/validation/latest/llms.txt>; use a concrete child page,
for example
<https://pydantic.dev/docs/validation/latest/api/pydantic-extra-types/pydantic_extra_types_phone_numbers/index.md>,
rather than guessing a root landing page.

For UUID version constraints, use the core Pydantic types API instead:
<https://pydantic.dev/docs/validation/latest/api/pydantic/types/index.md>.

## Usage and security

```python
from pydantic import BaseModel
from pydantic_extra_types.coordinate import Coordinate
from pydantic_extra_types.semantic_version import SemanticVersion

class Release(BaseModel):
    version: SemanticVersion
    location: Coordinate
```

These types validate format and often checksums; they do not authorize payments,
prove a phone number is reachable, or make an ISO code current after a library
upgrade. Constraints intended for Pydantic core types may not apply directly to
all extra types; add an explicit `Annotated` validator when a second invariant is
needed.

Treat `PaymentCardNumber` and `PhoneNumber` as sensitive personal data. Never log
the full value; use a masked/last-four representation where the type provides one.
Luhn/ABA/ISBN checks are format checks, not payment authorization. Treat
`ImportString` and environment-controlled type imports as executable configuration.

Check the exact module name for SemVer: current docs use
`pydantic_extra_types.semantic_version`; older `semver` imports may be deprecated.
