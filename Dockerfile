# ── ACI — Autonomous Company Interface ──────────────────────
# https://github.com/narko4u/aci-spec
# ghcr.io/narko4u/aci-spec

FROM python:3.12-slim AS builder

WORKDIR /app
RUN pip install --no-cache-dir aci-spec==0.9.0

# ── Runtime ─────────────────────────────────────────────────
FROM python:3.12-slim

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/aci-validate /usr/local/bin/aci-validate
COPY --from=builder /usr/local/bin/aci-explore /usr/local/bin/aci-explore

ENTRYPOINT ["aci-validate"]
CMD ["--help"]
