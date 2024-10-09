# Flying saw

Flying saw is a PLC utilizing [Zeugwerk Framewerk](https://doc.zeugwerk.dev). This demo application showcases how to implement a flying saw using the `MoveInterpolatedPositionAsync` method of *Zeugwerk Framework*'s axis interface. A python visualization provides a visual representation of real-time control.

In the demo, you can see three gears:

- In the Visualization, boxes spawn every 0.5s to 4s from the left whenever the conveyer is moving
- A sensor detects the boxes and set a digital input to true whenever it is blocked by a box
- The PLC picks up the signal and adds a 'box' object to a ringbuffer, which contains the timestamp of the boxes arrival
- The gripper will handle all boxes in the PLCs ringbuffer consecutively. It follows the boxes trajectory for 1.5s before moving to the next box in the ringbuffer

<div style="display: flex; justify-content: space-between;">
<img src="/Images/Peek 2024-10-09 21-47.gif"/>
</div>

## Requirements

To run this application, ensure you have the following installed:

- [TwinCAT]() >= 4024.xx
- [Zeugwerk Development Kit](https://doc.zeugwerk.dev/) >= 1.6
- Python 3.x (We recommend [Miniconda](https://docs.anaconda.com/miniconda/))


## Visualization

To run the Visualization in Windows a python distribution has to be installed (Anaconda or Miniconda is recommended).
With an installed python distribution, execute the following commands in the `Visualization` folder to prepare a virtual environment for python and install all requirements

```bash
pip install virtualenv
virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Activate the PLC and run the Visualization with 

```bash
python main.py
```

You can use the `Servicepanel`, which is integrated into Zeugwerk Creator to control the PLC.
