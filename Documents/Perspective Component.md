# THE NEW PERSPECTIVE COMPONENT

## New Grading System
The new version of the Perspective Component makes crucial changes to the grading system. 
The most important one being the seperation of some criterions.
**Starting today, the criterions will be seperated into two groups: Core and Extra.**
**This change was made to ensure fair grading as it can be hard for a computer program to evaluate advanced criterions.**

The Core criterions include **Horizon Line Detection**, **Vanishing Point Detection**,**Vanishing Line Detection** and **Horizontal/Vertical Line Detection**.
They're all fundamental aspects of perspective drawings and we're confident in the programs ability to assess these criterions correctly without any human intervention needed.

Extra Criterions, on the other hand, include **Light/Dark Balance** and **Colour Perspective**.
They are harder to calculate and assess by a computer program and their implementations vary heavily depending on the artist.
For example, the **Colour Perspective** criterion currently requires the user to choose an origin to start calculating from.

The points for the criterions have been changed as well to account for this seperation.

| Criterion | Group | Points |
|:----------|:------|:-------|
| Horizon Line  Detection |**Core** | *20* |
| Vanishing Point Detection | **Core** | *20* |
| Vanishing Line Detection | **Core** | *20* |
| Horizontal/Vertical Line Detection| **Core** | *20* |
| Light/Dark Balance | **Extra** | *10* |
| Colour Perspective | **Extra** | *10* |

## New User Interface
The user interface has been overhauled to work better with the new grading system.
Tags have been added to run the perspective component only with the desired criterions.
Running the component scan without tags result in the program grading the core criterions only.
This change was made to make it easier to develop the program.

The tags currently consist of "--criterions all", "--criterions core" and "--criterions extra".

