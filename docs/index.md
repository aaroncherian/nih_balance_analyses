# Analyzing Static Balance with FreeMoCap

This page documents our validation of the FreeMoCap system on the NIH Balance Assessment. 

<video width="300" height="550" controls>
  <source src="images/video_eo_fg.mp4" type="video/mp4">
Your browser does not support the video tag.
</video> 

##  Overview 
Patient balance and progress in rehabilitation is often measured using comprehensive  **qualitative** assessments. However, these tests 
tend to be **subjective** and may not be responsive to small changes in a patient. The ability to capture human movement data while 
performing these clinical assessments could provide clinicians with quantitative, standardized insight into patient movement 
capability. 

FreeMoCap is an **open-source, low-cost, markerless motion capture system** that leverages advancements in 
computer vision and machine learning to capture human movement data without specialized equipment.

To validate the suitability of FreeMoCap as a clinical assessment tool, we record participants performing the NIH Standing Balance Test (SBT). 
We then compare center of mass (COM) derived parameters based on 3D pose estimation from FreeMoCap to both 3D estimates from 
Qualisys, a marker-based system, and to the outcomes reported by the NIH BalancePod app. 

### Existing Technology and Limitations

Systems such as marker-based motion capture and force plates can provide highly accurate data, but they are extremely expensive and require specialized equipment, which often restricts their use to the laboratory environment. On the other hand, accelerometers are affordable and can be used to track real-world activities, but are limited in the information that they can provide about body position and orientation.

As such, there is a need for a **low-cost, accessible tool that could augment current rehabilitation practices by providing a comprehensive human movement data of a patient**


### The FreeMotionCapture Project (FreeMoCap)

FreeMoCap is an open-source, free, markerless motion capture system that leverages advancements in computer vision and machine learning to capture human movement data without specialized equipment.

insert all things about freemocap here

### Aim

Validate the Free Motion Capture Project (FreeMoCap), on a clinical balance assessment: the NIH Standing Balance Test (SBT)

### The NIH Standing Balance Test (SBT)

The NIH SBT is an assessment tool designed to evaluate an individual’s postural stability and balance. Participants stand feet together, and are asked to stand as still as possible for 50s under increasingly difficult conditions. These conditions include:

1) Standing with eyes **open** on **solid ground** <br>
2) Standing with eyes **closed** on **solid ground** <br>
3) Standing with eyes **open** on a **foam pad** <br>
4) Standing with eyes **closed** on a **foam pad** <br>

In a typical assessment, an accelerometer (usually an iPhone) is worn around the participant's waist. The accelerometer measures postural sway, which is then converted into a number of NIH scores that represent overall balance ability 

