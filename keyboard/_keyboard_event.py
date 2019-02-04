# -*- coding: utf-8 -*-
import Quartz
import LaunchServices
from Cocoa import NSURL
import Quartz.CoreGraphics as CG
from time import time as now
import json
from ._canonical_names import canonical_names, normalize_name

try:
    basestring
except NameError:
    basestring = str

KEY_DOWN = 'down'
KEY_UP = 'up'

def screenshot(path, region = None):
    """region should be a CGRect, something like:
    >>> import Quartz.CoreGraphics as CG
    >>> region = CG.CGRectMake(0, 0, 100, 100)
    >>> sp = ScreenPixel()
    >>> sp.capture(region=region)
    The default region is CG.CGRectInfinite (captures the full screen)
    """
    if region is None:
        region = CG.CGRectInfinite
    # Create screenshot as CGImage
    image = CG.CGWindowListCreateImage(
        region,
        CG.kCGWindowListOptionOnScreenOnly,
        CG.kCGNullWindowID,
        CG.kCGWindowImageDefault)
    dpi = 72 # FIXME: Should query this from somewhere, e.g for retina displays
    url = NSURL.fileURLWithPath_(path)
    dest = Quartz.CGImageDestinationCreateWithURL(
        url,
        LaunchServices.kUTTypePNG, # file type
        1, # 1 image in file
        None
        )
    properties = {
        Quartz.kCGImagePropertyDPIWidth: dpi,
        Quartz.kCGImagePropertyDPIHeight: dpi,
        }
    # Add the image to the destination, characterizing the image with
    # the properties dictionary.
    Quartz.CGImageDestinationAddImage(dest, image, properties)
    # When all the images (only 1 in this example) are added to the destination, 
    # finalize the CGImageDestination object. 
    Quartz.CGImageDestinationFinalize(dest)

class KeyboardEvent(object):
    event_type = None
    scan_code = None
    name = None
    time = None
    device = None
    modifiers = None
    is_keypad = None
    image = None

    def __init__(self, event_type, scan_code, name=None, time=None, device=None, modifiers=None, is_keypad=None, image=None):
        self.event_type = event_type
        self.scan_code = scan_code
        self.time = now() if time is None else time
        self.device = device
        self.is_keypad = is_keypad
        self.modifiers = modifiers
        self.image =  screenshot("%s.png" % now(), region=CG.CGRectMake(425, 47, 547, 326)) if image is None else image
        if name:
            self.name = normalize_name(name)

    def to_json(self, ensure_ascii=False):
        attrs = dict(
            (attr, getattr(self, attr)) for attr in ['event_type', 'scan_code', 'name', 'time', 'device', 'is_keypad']
            if not attr.startswith('_') and getattr(self, attr) is not None
        )
        return json.dumps(attrs, ensure_ascii=ensure_ascii)

    def __repr__(self):
        return 'KeyboardEvent({} {})'.format(self.name or 'Unknown {}'.format(self.scan_code), self.event_type)

    def __eq__(self, other):
        return (
            isinstance(other, KeyboardEvent)
            and self.event_type == other.event_type
            and (
                not self.scan_code or not other.scan_code or self.scan_code == other.scan_code
            ) and (
                not self.name or not other.name or self.name == other.name
            )
        )
