## Autogen Robot

This project showcases how LLM's can be built to control robot actions. Rather than deterministic input rules that dictate how the robot might move - for example pressing forward on the controller to initiate the walking action - the LLM brain of the robot knows what actions it can perform, and decide to put a number of combinations together to achieve a goal.

<center>

<img src="../../resources/img/robot.jpg" width=350/></img>

</center>

The intended goal is to control a robots motions using natural language.
The robot has different sets of motions called Actions (located in `/action_files`).
These can be used as function calls

**Future modifications to include:**
- Adding voice assisted interaction with the robot.
- Autonomous decision making