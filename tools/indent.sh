#!/bin/sh

indent	\
--blank-lines-after-declarations	\
--blank-lines-after-procedures		\
--braces-on-if-line		\
--braces-on-struct-decl-line	\
--cuddle-do-while		\
--cuddle-else			\
--case-indentation4		\
--no-tabs			\
--indent-level4			\
--continuation-indentation4	\
--no-space-after-function-call-names	\
--space-after-cast		\
--space-special-semicolon	\
--space-after-for		\
--space-after-if		\
--space-after-while		\
--declaration-indentation8	\
--no-blank-lines-after-commas	\
--line-length80			\
--dont-break-function-decl-args	\
--dont-break-procedure-type	\
--break-after-boolean-operator	\
--continue-at-parentheses	\
--no-space-after-parentheses	\
--indent-label1			\
$*
