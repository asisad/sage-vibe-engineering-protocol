# SAGE Bridge Standard

Bridges remain thin and provider-neutral. Their contract covers application
main-thread constraints, connection lifecycle, framing/serialization,
reconnect, timeout, cancellation, crash isolation, host/version compatibility,
localhost/network security, request-size limits, audit logging and safe
shutdown. A bridge MUST NOT expand permissions or mutate the approved scope.
