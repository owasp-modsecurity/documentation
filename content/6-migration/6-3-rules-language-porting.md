---
title: Rules language porting specification
weight: 3
---

This document's aim is to list the minimum ModSecurity Rules Language items which must be implemented by porting projects. These items are considered **Level 1: Core Features**. It may not be possible to properly implement all ModSecurity capabilities (Lua API, Persistent Storage, etc...) in porting efforts. These are considered **Level 2: Advanced Features**.

## Level 1: Core Features

The following ModSecurity Configuration and Rules Language items must be implemented by porting efforts.

### Directives

- SecRuleEngine
- SecRule
- SecRequestBody Access
- SecResponseBodyAccess

### Variables

- ARGS
- ARGS_NAMES
- QUERY_STRING
- REMOTE_ADDR
- REQUEST_BASENAME
- REQUEST_BODY
- REQUEST_COOKIES
- REQUEST_COOKIES_NAMES
- REQUEST_FILENAME
- REQUEST_HEADERS
- REQUEST_HEADERS_NAMES
- REQUEST_METHOD
- REQUEST_PROTOCOL
- REQUEST_URI
- RESPONSE_BODY
- RESPONSE_CONTENT_LENGTH
- RESPONSE_CONTENT_TYPE
- RESPONSE_HEADERS
- RESPONSE_HEADERS_NAMES
- RESPONSE_PROTOCOL
- RESPONSE_STATUS

### Operators

- rx
- eq
- ge
- gt
- le
- lt

### Actions

- allow
- msg
- id
- rev
- severity
- log
- deny
- block
- status
- phase
- t
- skip
- chain

### Transformation Functions

- lowercase
- urlDecode
- none
- compressWhitespace
- removeWhitespace
- replaceNulls
- removeNulls

### Phases

- phase:1 - Request headers stage
- phase:2 - Request body stage
- phase:3 - Response headers stage
- phase:4 - Response body stage

## Level 2: Advanced Features
