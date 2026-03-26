# syntax=docker/dockerfile:1.4

# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# Gemini CLI sandbox image for OpenShell
#
# Builds on the community base sandbox and adds Google Gemini CLI.
# Build:  docker build -t openshell-gemini --build-arg BASE_IMAGE=openshell-base .
# Run:    openshell sandbox create --from gemini

ARG BASE_IMAGE=ghcr.io/nvidia/openshell-community/sandboxes/base:latest
FROM ${BASE_IMAGE}

USER root

# Copy sandbox policy
COPY policy.yaml /etc/openshell/policy.yaml

USER sandbox

ENTRYPOINT ["/bin/bash"]