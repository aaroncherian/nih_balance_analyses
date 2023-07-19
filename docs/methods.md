# Methods

## Task: The NIH Standing Balance Test (SBT) 
Participants were asked to complete three trials of the NIH SBT. For each condition, participants were instructed to stand as still as possible for 55 seconds, keeping their gaze fixated on a specific point, feet together and arms held at their side. Participants were recorded using three different systems, detailed below. 

## Tracking Patient Motion
### NIH BalancePod App
An iPhone was worn around the participants' waists. The iPhone was connected via Bluetooth to an iPad running the NIH Toolbox app, which was used to administer the Standing Balance Test.  

### Qualisys
Retroreflective markers were placed on the participant, and a Qualisys marker-based system was used to capture motion capture data

### FreeMoCap
Six webcams were set up around the subject. Cameras were calibrated, and then used to record the patient during the SBT. 

## Data Analysis

### Reconstructing 3D Data
Synchronized videos from the webcams were fed through the FreeMoCap software to reconstruct 3D joint centers. FreeMoCap data was smoothed using a low-pass, 4th order, 6Hz Butterworth filter. Qualisys data was downsampled and time-synchronized with FreeMoCap data. Specific frames were annotated for the start and end point of each balance 
condition within the recording. 1600 frames were analyzed for each condition. 

### Center of Mass Calculation
For both systems, segment and total body center of mass was calculated using anthropometric data. For each condition, the overall path length of the center of mass was calculated. Center of mass position was also used to calculate center of mass velocity as well during each condition. 