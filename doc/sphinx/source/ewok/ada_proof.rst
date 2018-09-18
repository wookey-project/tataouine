Summary of SPARK analysis
=========================

============================= ======== ========= ========== ========== =========== =========== =========
SPARK Analysis results        Total        Flow   Interval   CodePeer     Provers   Justified   Unproved
============================= ======== ========= ========== ========== =========== =========== =========
Data Dependencies                 .           .          .          .           .           .          .
Flow Dependencies                 .           .          .          .           .           .          .
Initialization                   75          75          .          .           .           .          .
Non-Aliasing                      .           .          .          .           .           .          .
Run-time Checks                   5           .          .          .      5 (Z3)           .          .
Assertions                        3           .          .          .      2 (Z3)           .          1
Functional Contracts             21           .          .          .     15 (Z3)           .          6
LSP Verification                  .           .          .          .           .           .          .
Total                           104    75 (72%)          .          .    22 (21%)           .     7 (7%)
============================= ======== ========= ========== ========== =========== =========== =========

