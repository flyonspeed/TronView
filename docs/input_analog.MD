
## Analog CDI from IFR Navigator

  TronView supports reading CDI and VDI data from an IFR Navigator for use on EFIS systems that do not output this data over RS-232. This is done via the ADS 1115 Analog to Digital Converting I2C chip from Texas Instruments. The ADS 1115 is available on a carrier board from Adafruit to make connecting to it more convenient with a Pi.

  This interface enables a "crosshair" style presentation of CDI data on the defaul and F18 hud pages, plus any page you may come up with. This essentially creates the ability for one to fly an ILS or GPS/LPV approach using TronView, though since TronView is NOT a certified instrument nor is it intended in any way to be used as primary instrumentation.

  In order to wire this up, you'll need an IFR navigator (GPS or NAV radio) that supports the output of +L/+R and +U/+D signals. Examples of radios that do this include the Garmin GNS, GTN and 2-inch GPS Navigator series, Garmin GNC 255/215, SL-30, Avidyne IFD and King KX 165 (NOT 155) units. There are certainly more that will do this, but these are the most popular examples.

  This hookup uses the same wiring as most mechanical CDIs.

  The ADC has 4 input channels, labeled 0-3. Channel 0 is CDI +L, Channel 1 is CDI +R, Channel 2 is VDI +U, and Channel 3 is VDI +D. Refer to your navgiator's installation manual/pinout to determine the matching pins. 

  We recommend installing an intermediate D-Sub connector for both diagnostics and future changes.

