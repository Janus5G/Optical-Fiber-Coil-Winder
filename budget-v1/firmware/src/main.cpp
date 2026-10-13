#define STANDARD_MACHINE 0
#define ENABLE_REAL_MOTION 0  // hard safety build lock: physical tests REQUIRED before change
#include "../../../common/controller/embedded/winder.hpp"
winder::Winder machine;
void setup(){machine.begin();}
void loop(){machine.tick();}
