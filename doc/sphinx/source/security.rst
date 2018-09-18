Security concerns and principles behind WooKey
==============================================

The security model is based on both hardware and software primitives
designed to bring in-depth security.

Hardware security relies on an extractable token embedding a secure
element. This token is meant to provide a pre-boot authentication feature
as well as a secure storage area for the sensitive master keys of WooKey
user data encryption.

Software security relies on a microkernel that enforces privilege separation,
memory isolation, W⊕X principle, stack and heap anti-smashing
techniques. The most sensitive parts are implemented with a safe language
(SPARK/Ada).

The secure update mechanism over USB is based on the DFU (Device
Firmware Update) protocol. It also uses the pre-boot user authentication
feature to strengthen the security of the platform. Firmware integrity
and authenticity are based on state of the art cryptography.
