# Code and credential provenance

This repository is GPL-3.0-only. The complete license is in [LICENSE](LICENSE).

- `scripts/bpkit/protocol.py` is a cleaned-up derivative of the local prototype developed for this workflow, informed by `youcci/playport`'s GPL-3.0 protocol implementation (itself ported from `shihabal3amri/DiPlay` and `shilapi/xcertplay`). See the [PlayPort source](https://github.com/youcci/playport). The baseline protocol source was inspected at commit recorded in `references/source-versions.json`.
- `scripts/local_mfi_v3_helper.py`, `scripts/import_diplay_identity.py`, and `scripts/local-only.sb` are copied/adapted from [aur3l14no/accessory-location](https://github.com/aur3l14no/accessory-location), commit `8a13296a3d81dae18ad4481e7a9eca913c2c644f`, GPL-3.0-only. The importer default data directory was changed. Import tests are adapted from that project; signing tests use the same synthetic-identity technique. The code retains its original docstrings. This project adds the skill workflow, local process supervision/evidence, phone-clock alignment, packaging, and installation.
- Python dependencies have their own licenses; resolved packages are pinned in `uv.lock`. No third-party dependencies or binaries are embedded in the release ZIPs.

## Identity material is NOT included or relicensed

The optional DiPlay v0.2.7 APK source is documented by the upstream projects as a shared experimental identity recovered from public Carlinkit C2Air firmware. It was not issued to this project. It is separate third-party credential material, **not** GPL source code. Do not commit, upload, redistribute, or sell it. Using it is a separate local choice; Apple can reject or revoke it.

The importer downloads the pinned public APK only when explicitly requested, checks its full SHA-256 (`27b434462da7e78b1ff0987d129ed0a4b0a0e56beceaf8ec221d47150d4675bd`), and extracts two bounded assets to an owner-only directory outside the checkout. It does not install or execute the APK. Temporary download data is discarded. A self-signed test identity is never presented as trusted by Apple.

[DiPlay third-party notice](https://github.com/shihabal3amri/DiPlay/blob/main/docs/THIRD_PARTY_NOTICES.md#experimental-authentication-data) · [DiPlay v0.2.7 release](https://github.com/shihabal3amri/DiPlay/releases/tag/v0.2.7)

Apple, Apple Watch, iPhone, CarPlay and MFi are trademarks of Apple Inc. This project is independent and is not an Apple-certified accessory or medical product.
