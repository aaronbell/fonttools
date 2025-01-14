"""
Define all configuration options that can affect the working of fontTools
modules. E.g. optimization levels of varLib IUP, otlLib GPOS compression level,
etc. If this file gets too big, split it into smaller files per-module.

An instance of the Config class can be attached to a TTFont object, so that
the various modules can access their configuration options from it.
"""
from textwrap import dedent

from fontTools.misc.configTools import *


class Config(AbstractConfig):
    options = Options()

OPTIONS = Config.options

Config.register_option(
    name="fontTools.otlLib.optimize.gpos:COMPRESSION_LEVEL",
    help=dedent(
        """\
        GPOS Lookup type 2 (PairPos) compression level:
            0 = do not attempt to compact PairPos lookups;
            1 to 8 = create at most 1 to 8 new subtables for each existing
                subtable, provided that it would yield a 50%% file size saving;
            9 = create as many new subtables as needed to yield a file size saving.
        Default: 0.

        This compaction aims to save file size, by splitting large class
        kerning subtables (Format 2) that contain many zero values into
        smaller and denser subtables. It's a trade-off between the overhead
        of several subtables versus the sparseness of one big subtable.

        See the pull request: https://github.com/fonttools/fonttools/pull/2326
        """
    ),
    default=0,
    parse=int,
    validate=lambda v: v in range(10),
)
