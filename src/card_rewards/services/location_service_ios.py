from dataclasses import dataclass
from typing import Callable, Optional

from rubicon.objc import NSObject, objc_method
from rubicon.objc import ObjCClass

CLLocationManager = ObjCClass("CLLocationManager")

@dataclass(frozen=True)
class Location:
    lat: float
    lng: float
    accuracy_m: Optional[float]

class _LocationDelegate(NSObject):
    def initWithCallback_(self, callback):
        self = _LocationDelegate.alloc().init()
        self._callback = callback
        return self

    @objc_method
    def locationManager_didUpdateLocations_(self, manager, locations) -> None:
        loc = locations.lastObject()
        coord = loc.coordinate
        acc = float(loc.horizontalAccuracy)
        self._callback(Location(lat=float(coord.latitude), lng=float(coord.longitude), accuracy_m=acc))

    @objc_method
    def locationManager_didFailWithError_(self, manager, error) -> None:
        # In production: propagate error to UI/logs.
        pass

class IOSLocationService:
    def __init__(self):
        self.manager = CLLocationManager.alloc().init()
        self.delegate = None

    def request_and_start(self, on_fix: Callable[[Location], None]):
        self.delegate = _LocationDelegate.alloc().initWithCallback_(on_fix)
        self.manager.setDelegate_(self.delegate)

        # Requires Info.plist: NSLocationWhenInUseUsageDescription
        self.manager.requestWhenInUseAuthorization()

        # ~10m accuracy; tune for battery vs precision
        self.manager.setDesiredAccuracy_(10.0)
        self.manager.startUpdatingLocation()

    def stop(self):
        self.manager.stopUpdatingLocation()
