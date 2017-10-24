"""PyDM State Button Class."""

from pydm.PyQt.QtGui import QPainter, QStyleOption, QAbstractButton
from pydm.PyQt.QtCore import pyqtProperty, Q_ENUMS, QByteArray, QRectF, QSize
from pydm.PyQt.QtSvg import QSvgRenderer
from pydm.widgets.base import PyDMWritableWidget


BUTTONSHAPE = {'Squared': 0, 'Rounded': 1}


class PyDMStateButton(QAbstractButton, PyDMWritableWidget):
    """
    A StateButton with support for Channels and much more from PyDM.

    It consists on QPushButton with internal state.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    init_channel : str, optional
        The channel to be used by the widget.
    """

    class buttonShapeMap:
        """Enum class of shapes of button."""

        locals().update(**BUTTONSHAPE)

    Q_ENUMS(buttonShapeMap)

    # enumMap for buttonShapeMap
    locals().update(**BUTTONSHAPE)

    squaredbuttonstatesdict = {
                            'On': """
                                  <svg
                                       xmlns:osb="http://www.openswatchbook.org/uri/2009/osb"
                                       xmlns:dc="http://purl.org/dc/elements/1.1/"
                                       xmlns:cc="http://creativecommons.org/ns#"
                                       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                                       xmlns:svg="http://www.w3.org/2000/svg"
                                       xmlns="http://www.w3.org/2000/svg"
                                       xmlns:xlink="http://www.w3.org/1999/xlink"
                                       xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
                                       xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
                                       width="256"
                                       height="129"
                                       viewBox="0 0 67.73248 34.13082"
                                       version="1.1"
                                       id="svg8"
                                       inkscape:version="0.92.1 unknown"
                                       sodipodi:docname="SquaredOnButton.svg">
                                      <defs
                                         id="defs2">
                                        <linearGradient
                                           inkscape:collect="always"
                                           id="linearGradient4625">
                                          <stop
                                             style="stop-color:#99ff55;stop-opacity:1;"
                                             offset="0"
                                             id="stop4621" />
                                          <stop
                                             style="stop-color:#99ff55;stop-opacity:0;"
                                             offset="1"
                                             id="stop4623" />
                                        </linearGradient>
                                        <linearGradient
                                           inkscape:collect="always"
                                           id="linearGradient4617">
                                          <stop
                                             style="stop-color:#66ff00;stop-opacity:1;"
                                             offset="0"
                                             id="stop4613" />
                                          <stop
                                             style="stop-color:#66ff00;stop-opacity:0;"
                                             offset="1"
                                             id="stop4615" />
                                        </linearGradient>
                                        <linearGradient
                                           id="linearGradient46973"
                                           osb:paint="gradient">
                                          <stop
                                             style="stop-color:#000000;stop-opacity:1;"
                                             offset="0"
                                             id="stop46969" />
                                          <stop
                                             style="stop-color:#000000;stop-opacity:0;"
                                             offset="1"
                                             id="stop46971" />
                                        </linearGradient>
                                        <linearGradient
                                           id="linearGradient46862"
                                           osb:paint="solid">
                                          <stop
                                             style="stop-color:#ececec;stop-opacity:1;"
                                             offset="0"
                                             id="stop46860" />
                                        </linearGradient>
                                        <linearGradient
                                           inkscape:collect="always"
                                           id="linearGradient47117">
                                          <stop
                                             style="stop-color:#cccccc;stop-opacity:1;"
                                             offset="0"
                                             id="stop47113" />
                                          <stop
                                             style="stop-color:#cccccc;stop-opacity:0;"
                                             offset="1"
                                             id="stop47115" />
                                        </linearGradient>
                                        <linearGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="linearGradient47119-6-3"
                                           x1="41.2561"
                                           y1="248.90253"
                                           x2="41.214836"
                                           y2="256.65088"
                                           gradientUnits="userSpaceOnUse"
                                           gradientTransform="matrix(0.89734862,-1.5002197e-8,1.251636e-8,0.99798917,10.92258,17.782472)" />
                                        <linearGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="linearGradient47119-5"
                                           x1="41.2561"
                                           y1="248.90253"
                                           x2="41.067112"
                                           y2="255.32812"
                                           gradientUnits="userSpaceOnUse"
                                           gradientTransform="matrix(0.89737573,0,0,0.99799499,-88.935698,-541.14417)" />
                                        <radialGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient4617"
                                           id="radialGradient44460-2"
                                           cx="27.781246"
                                           cy="262.60416"
                                           fx="27.781246"
                                           fy="262.60416"
                                           r="33.337498"
                                           gradientTransform="matrix(1.7352948,0.01419348,-0.00404564,0.49340261,-13.280746,149.6082)"
                                           gradientUnits="userSpaceOnUse" />
                                        <radialGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient4625"
                                           id="radialGradient4627"
                                           cx="23.017721"
                                           cy="353.20093"
                                           fx="23.017721"
                                           fy="353.20093"
                                           r="33.071649"
                                           gradientTransform="matrix(0.99996639,0.00819926,-0.00407819,0.49736889,12.288978,103.71221)"
                                           gradientUnits="userSpaceOnUse" />
                                      </defs>
                                      <sodipodi:namedview
                                         id="base"
                                         pagecolor="#ffffff"
                                         bordercolor="#666666"
                                         borderopacity="1.0"
                                         inkscape:pageopacity="0.0"
                                         inkscape:pageshadow="2"
                                         inkscape:zoom="1.4"
                                         inkscape:cx="80.712392"
                                         inkscape:cy="41.77284"
                                         inkscape:document-units="px"
                                         inkscape:current-layer="layer1"
                                         showgrid="false"
                                         units="px"
                                         inkscape:window-width="1916"
                                         inkscape:window-height="1057"
                                         inkscape:window-x="3840"
                                         inkscape:window-y="1080"
                                         inkscape:window-maximized="0" />
                                      <metadata
                                         id="metadata5">
                                        <rdf:RDF>
                                          <cc:Work
                                             rdf:about="">
                                            <dc:format>image/svg+xml</dc:format>
                                            <dc:type
                                               rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
                                            <dc:title />
                                          </cc:Work>
                                        </rdf:RDF>
                                      </metadata>
                                      <g
                                         inkscape:label="Layer 1"
                                         inkscape:groupmode="layer"
                                         id="layer1"
                                         transform="translate(0,-262.86875)">
                                        <rect
                                           style="opacity:1;fill:#666666;stroke-width:0.26431346"
                                           id="rect42330-9"
                                           width="67.731026"
                                           height="33.798767"
                                           x="0"
                                           y="263.20081"
                                           rx="3.9998636"
                                           ry="3.9919798" />
                                        <rect
                                           style="opacity:1;fill:#b3b3b3;stroke-width:0.29037237"
                                           id="rect42330-3-1"
                                           width="67.731026"
                                           height="32.74255"
                                           x="0"
                                           y="263.20081"
                                           rx="3.9998636"
                                           ry="3.9919798" />
                                        <rect
                                           ry="3.925447"
                                           rx="3.9681182"
                                           y="263.99298"
                                           x="0.79372311"
                                           height="31.158237"
                                           width="66.143578"
                                           id="rect42373-2"
                                           style="opacity:1;fill:#00aa00;fill-opacity:1;stroke-width:0.27992097" />
                                        <rect
                                           ry="3.9607925"
                                           rx="3.9686146"
                                           y="263.86902"
                                           x="0.93407822"
                                           height="31.406181"
                                           width="65.862862"
                                           id="rect42373-3-7"
                                           style="opacity:1;fill:url(#radialGradient4627);fill-opacity:1;stroke:url(#radialGradient44460-2);stroke-width:0.28043568;stroke-opacity:0.93956042" />
                                        <rect
                                           style="opacity:1;fill:#0c5a00;fill-opacity:1;stroke-width:0.18395628"
                                           id="rect42330-6-0"
                                           width="33.866241"
                                           height="32.742535"
                                           x="33.621384"
                                           y="263.13336"
                                           rx="3.5327301"
                                           ry="3.8672287" />
                                        <rect
                                           style="opacity:1;fill:#b3b3b3;stroke-width:0.20278068"
                                           id="rect42330-3-2-9"
                                           width="33.031647"
                                           height="32.74255"
                                           x="34.455971"
                                           y="263.13333"
                                           rx="3.4456699"
                                           ry="3.9919796" />
                                        <rect
                                           style="opacity:1;fill:#ececec;stroke-width:0.19357017"
                                           id="rect42330-3-2-2-36"
                                           width="31.629593"
                                           height="31.158237"
                                           x="35.03175"
                                           y="263.86902"
                                           rx="3.2994161"
                                           ry="3.7988195" />
                                        <rect
                                           transform="scale(-1)"
                                           ry="1.6487614"
                                           rx="3.1136119"
                                           y="-293.09921"
                                           x="-65.828644"
                                           height="13.52328"
                                           width="29.848389"
                                           id="rect42330-3-2-2-3-0"
                                           style="opacity:1;fill:url(#linearGradient47119-5);fill-opacity:1;stroke-width:0.12388156" />
                                        <rect
                                           style="opacity:1;fill:url(#linearGradient47119-6-3);fill-opacity:1;stroke-width:0.12387931"
                                           id="rect42330-3-2-2-3-2-6"
                                           width="29.847486"
                                           height="13.523202"
                                           x="34.028965"
                                           y="265.8259"
                                           rx="3.113518"
                                           ry="1.6487517"
                                           transform="matrix(0.99996239,-0.00867248,0.00701146,0.99997542,0,0)" />
                                      </g>
                                    </svg>

                                  """,
                            'Off': """
                                    <svg
                                       xmlns:osb="http://www.openswatchbook.org/uri/2009/osb"
                                       xmlns:dc="http://purl.org/dc/elements/1.1/"
                                       xmlns:cc="http://creativecommons.org/ns#"
                                       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                                       xmlns:svg="http://www.w3.org/2000/svg"
                                       xmlns="http://www.w3.org/2000/svg"
                                       xmlns:xlink="http://www.w3.org/1999/xlink"
                                       xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
                                       xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
                                       width="256"
                                       height="129"
                                       viewBox="0 0 67.73248 34.13082"
                                       version="1.1"
                                       id="svg8"
                                       inkscape:version="0.92.1 unknown"
                                       sodipodi:docname="SquaredOffButton.svg">
                                      <defs
                                         id="defs2">
                                        <linearGradient
                                           id="linearGradient7812"
                                           inkscape:collect="always">
                                          <stop
                                             id="stop7808"
                                             offset="0"
                                             style="stop-color:#0c5a00;stop-opacity:1;" />
                                          <stop
                                             id="stop7810"
                                             offset="1"
                                             style="stop-color:#0caa00;stop-opacity:0" />
                                        </linearGradient>
                                        <linearGradient
                                           inkscape:collect="always"
                                           id="linearGradient7744">
                                          <stop
                                             style="stop-color:#0c5a00;stop-opacity:1;"
                                             offset="0"
                                             id="stop7740" />
                                          <stop
                                             style="stop-color:#0caa00;stop-opacity:0"
                                             offset="1"
                                             id="stop7742" />
                                        </linearGradient>
                                        <linearGradient
                                           id="linearGradient46973"
                                           osb:paint="gradient">
                                          <stop
                                             style="stop-color:#000000;stop-opacity:1;"
                                             offset="0"
                                             id="stop46969" />
                                          <stop
                                             style="stop-color:#000000;stop-opacity:0;"
                                             offset="1"
                                             id="stop46971" />
                                        </linearGradient>
                                        <linearGradient
                                           id="linearGradient46862"
                                           osb:paint="solid">
                                          <stop
                                             style="stop-color:#ececec;stop-opacity:1;"
                                             offset="0"
                                             id="stop46860" />
                                        </linearGradient>
                                        <radialGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient7812"
                                           id="radialGradient44460"
                                           cx="29.12948"
                                           cy="262.3385"
                                           fx="29.12948"
                                           fy="262.3385"
                                           r="33.337498"
                                           gradientTransform="matrix(1.2611815,8.8607088e-5,-1.7345295e-4,0.42019145,-0.84900691,169.17349)"
                                           gradientUnits="userSpaceOnUse" />
                                        <linearGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="linearGradient47119"
                                           x1="41.2561"
                                           y1="248.90253"
                                           x2="41.067112"
                                           y2="255.32812"
                                           gradientUnits="userSpaceOnUse"
                                           gradientTransform="matrix(1.0160577,0,0,0.99998734,-62.006121,-541.86296)" />
                                        <linearGradient
                                           inkscape:collect="always"
                                           id="linearGradient47117">
                                          <stop
                                             style="stop-color:#cccccc;stop-opacity:1;"
                                             offset="0"
                                             id="stop47113" />
                                          <stop
                                             style="stop-color:#cccccc;stop-opacity:0;"
                                             offset="1"
                                             id="stop47115" />
                                        </linearGradient>
                                        <linearGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="linearGradient47119-6"
                                           x1="41.2561"
                                           y1="248.90253"
                                           x2="41.214836"
                                           y2="256.65088"
                                           gradientUnits="userSpaceOnUse"
                                           gradientTransform="matrix(1.0160187,1.8494609e-8,-1.7616317e-8,0.99998834,-26.320612,17.159684)" />
                                        <radialGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient7744"
                                           id="radialGradient7746"
                                           cx="28.309671"
                                           cy="263.13199"
                                           fx="28.309669"
                                           fy="263.13199"
                                           r="32.525963"
                                           gradientTransform="matrix(1.2926485,9.0634671e-5,-1.7773177e-4,0.43067548,-0.70463684,166.08141)"
                                           gradientUnits="userSpaceOnUse" />
                                      </defs>
                                      <sodipodi:namedview
                                         id="base"
                                         pagecolor="#ffffff"
                                         bordercolor="#666666"
                                         borderopacity="1.0"
                                         inkscape:pageopacity="0.0"
                                         inkscape:pageshadow="2"
                                         inkscape:zoom="0.98994949"
                                         inkscape:cx="59.865723"
                                         inkscape:cy="191.47843"
                                         inkscape:document-units="px"
                                         inkscape:current-layer="layer1"
                                         showgrid="false"
                                         units="px"
                                         inkscape:window-width="1916"
                                         inkscape:window-height="1057"
                                         inkscape:window-x="3840"
                                         inkscape:window-y="0"
                                         inkscape:window-maximized="0" />
                                      <metadata
                                         id="metadata5">
                                        <rdf:RDF>
                                          <cc:Work
                                             rdf:about="">
                                            <dc:format>image/svg+xml</dc:format>
                                            <dc:type
                                               rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
                                            <dc:title />
                                          </cc:Work>
                                        </rdf:RDF>
                                      </metadata>
                                      <g
                                         inkscape:label="Layer 1"
                                         inkscape:groupmode="layer"
                                         id="layer1"
                                         transform="translate(0,-262.86875)">
                                        <rect
                                           style="opacity:1;fill:#666666;stroke-width:0.26458001"
                                           id="rect42330"
                                           width="67.732483"
                                           height="33.866241"
                                           x="4.0228883e-08"
                                           y="263.13333"
                                           rx="3.9999495"
                                           ry="3.9999495" />
                                        <rect
                                           style="opacity:1;fill:#b3b3b3;stroke-width:0.29066521"
                                           id="rect42330-3"
                                           width="67.732483"
                                           height="32.807919"
                                           x="4.0228883e-08"
                                           y="263.13333"
                                           rx="3.9999495"
                                           ry="3.9999495" />
                                        <rect
                                           ry="3.9332836"
                                           rx="3.9682035"
                                           y="263.92709"
                                           x="0.79374027"
                                           height="31.22044"
                                           width="66.144997"
                                           id="rect42373"
                                           style="opacity:1;fill:#112b0b;fill-opacity:1;stroke-width:0.28020325" />
                                        <rect
                                           ry="3.9686997"
                                           rx="3.9686997"
                                           y="263.98401"
                                           x="0.93555796"
                                           height="31.220446"
                                           width="66.003174"
                                           id="rect42373-3"
                                           style="opacity:1;fill:url(#radialGradient7746);fill-opacity:1;stroke:url(#radialGradient44460);stroke-width:0;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:0.93956042" />
                                        <g
                                           id="g5809"
                                           transform="scale(0.88319365,1)">
                                          <rect
                                             transform="scale(-1)"
                                             ry="3.874949"
                                             rx="3.9999495"
                                             y="-295.9415"
                                             x="-38.345203"
                                             height="32.807903"
                                             width="38.345203"
                                             id="rect42330-6"
                                             style="opacity:1;fill:#2d0000;fill-opacity:1;stroke-width:0.1959385" />
                                          <rect
                                             transform="scale(-1)"
                                             ry="3.9999492"
                                             rx="3.9013755"
                                             y="-295.94153"
                                             x="-37.400234"
                                             height="32.807919"
                                             width="37.400234"
                                             id="rect42330-3-2"
                                             style="opacity:1;fill:#b3b3b3;stroke-width:0.21598901" />
                                          <rect
                                             transform="scale(-1)"
                                             ry="3.8064034"
                                             rx="3.7357788"
                                             y="-295.20444"
                                             x="-36.74831"
                                             height="31.22044"
                                             width="35.812752"
                                             id="rect42330-3-2-2"
                                             style="opacity:1;fill:#ececec;stroke-width:0.20617858" />
                                          <path
                                             inkscape:connector-curvature="0"
                                             id="path47770"
                                             d="m 34.653293,295.81587 c 1.202283,-0.40774 2.117931,-1.32505 2.568609,-2.57327 l 0.218932,-0.60637 0.02726,-12.56756 c 0.01741,-8.03127 -0.0071,-12.85035 -0.06793,-13.35106 -0.132866,-1.0937 -0.497502,-1.82283 -1.275617,-2.55072 -0.385387,-0.36052 -0.793099,-0.64034 -1.110913,-0.76244 -0.409461,-0.15731 -0.453593,-0.19381 -0.239241,-0.19782 0.401868,-0.008 1.330211,0.33664 1.912157,0.70891 0.59553,0.38095 1.079958,0.98807 1.390754,1.74298 l 0.213966,0.51971 v 13.32349 c 0,12.6785 -0.0084,13.34756 -0.173324,13.82069 -0.459914,1.3193 -1.798816,2.35087 -3.275664,2.52378 -0.303577,0.0355 -0.357641,0.0269 -0.188987,-0.0303 z"
                                             style="opacity:1;fill:#17280b;fill-opacity:1;fill-rule:evenodd;stroke:none;stroke-width:0.1006349;stroke-linecap:round;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;paint-order:stroke fill markers" />
                                          <rect
                                             style="opacity:1;fill:url(#linearGradient47119);fill-opacity:1;stroke-width:0.13195072"
                                             id="rect42330-3-2-2-3"
                                             width="33.795975"
                                             height="13.550277"
                                             x="-35.843052"
                                             y="-293.32275"
                                             rx="3.5254014"
                                             ry="1.6520529"
                                             transform="scale(-1)" />
                                          <rect
                                             transform="matrix(0.99997055,-0.00767484,0.00792289,0.99996861,0,0)"
                                             ry="1.6520544"
                                             rx="3.5252662"
                                             y="265.7001"
                                             x="-0.15851437"
                                             height="13.55029"
                                             width="33.794678"
                                             id="rect42330-3-2-2-3-2"
                                             style="opacity:1;fill:url(#linearGradient47119-6);fill-opacity:1;stroke-width:0.13194825" />
                                        </g>
                                      </g>
                                    </svg>
                                   """,
                            'Disconnected': """
                                    <svg
                                       xmlns:dc="http://purl.org/dc/elements/1.1/"
                                       xmlns:cc="http://creativecommons.org/ns#"
                                       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                                       xmlns:svg="http://www.w3.org/2000/svg"
                                       xmlns="http://www.w3.org/2000/svg"
                                       xmlns:xlink="http://www.w3.org/1999/xlink"
                                       xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
                                       xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
                                       width="256"
                                       height="129"
                                       viewBox="0 0 67.733331 34.131251"
                                       version="1.1"
                                       id="svg159"
                                       inkscape:version="0.92.1 unknown"
                                       sodipodi:docname="SquaredDisconnectButton.svg">
                                      <defs
                                         id="defs153">
                                        <linearGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="linearGradient47119-6"
                                           x1="41.2561"
                                           y1="248.90253"
                                           x2="41.214836"
                                           y2="256.65088"
                                           gradientUnits="userSpaceOnUse"
                                           gradientTransform="matrix(0.88273561,1.8213812e-8,-1.4296e-8,0.99999332,-5.5262653,17.145788)" />
                                        <linearGradient
                                           inkscape:collect="always"
                                           id="linearGradient47117">
                                          <stop
                                             style="stop-color:#cccccc;stop-opacity:1;"
                                             offset="0"
                                             id="stop47113" />
                                          <stop
                                             style="stop-color:#cccccc;stop-opacity:0;"
                                             offset="1"
                                             id="stop47115" />
                                        </linearGradient>
                                        <linearGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="linearGradient47119"
                                           x1="41.2561"
                                           y1="248.90253"
                                           x2="41.067112"
                                           y2="255.32812"
                                           gradientUnits="userSpaceOnUse"
                                           gradientTransform="matrix(0.88276109,0,0,0.99999997,-71.212313,-541.70269)" />
                                        <radialGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="radialGradient44460"
                                           cx="27.781246"
                                           cy="262.60416"
                                           fx="27.781246"
                                           fy="262.60416"
                                           r="33.337498"
                                           gradientTransform="matrix(1.176961,2.4123198e-7,-8.8978764e-8,0.41608433,1.1684521,170.27202)"
                                           gradientUnits="userSpaceOnUse" />
                                        <radialGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="radialGradient8012"
                                           cx="33.865871"
                                           cy="279.53751"
                                           fx="33.865871"
                                           fy="279.53751"
                                           r="33.072918"
                                           gradientTransform="matrix(1.1863765,3.4113101e-7,-1.1988375e-7,0.41941276,-6.3117695,162.29589)"
                                           gradientUnits="userSpaceOnUse" />
                                      </defs>
                                      <sodipodi:namedview
                                         id="base"
                                         pagecolor="#ffffff"
                                         bordercolor="#666666"
                                         borderopacity="1.0"
                                         inkscape:pageopacity="0.0"
                                         inkscape:pageshadow="2"
                                         inkscape:zoom="1.7167969"
                                         inkscape:cx="-104.29494"
                                         inkscape:cy="92.021553"
                                         inkscape:document-units="px"
                                         inkscape:current-layer="layer1"
                                         showgrid="false"
                                         units="px"
                                         inkscape:window-width="1916"
                                         inkscape:window-height="1057"
                                         inkscape:window-x="3840"
                                         inkscape:window-y="0"
                                         inkscape:window-maximized="0" />
                                      <metadata
                                         id="metadata156">
                                        <rdf:RDF>
                                          <cc:Work
                                             rdf:about="">
                                            <dc:format>image/svg+xml</dc:format>
                                            <dc:type
                                               rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
                                            <dc:title />
                                          </cc:Work>
                                        </rdf:RDF>
                                      </metadata>
                                      <g
                                         inkscape:label="Layer 1"
                                         inkscape:groupmode="layer"
                                         id="layer1"
                                         transform="translate(0,-262.86873)">
                                        <rect
                                           style="opacity:1;fill:#666666;stroke-width:0.26458332"
                                           id="rect42330"
                                           width="67.73333"
                                           height="33.866665"
                                           x="1.110223e-16"
                                           y="263.1333"
                                           rx="3.9999998"
                                           ry="3.9999998" />
                                        <rect
                                           style="opacity:1;fill:#b3b3b3;stroke-width:0.29066887"
                                           id="rect42330-3"
                                           width="67.73333"
                                           height="32.808334"
                                           x="1.110223e-16"
                                           y="263.1333"
                                           rx="3.9999998"
                                           ry="3.9999998" />
                                        <rect
                                           ry="3.9333332"
                                           rx="3.9682536"
                                           y="263.92706"
                                           x="0.79370123"
                                           height="31.220833"
                                           width="66.145836"
                                           id="rect42373"
                                           style="opacity:1;fill:#333333;fill-opacity:1;stroke-width:0.28020677" />
                                        <rect
                                           ry="3.96875"
                                           rx="3.96875"
                                           y="263.80286"
                                           x="0.9333176"
                                           height="31.469278"
                                           width="65.865112"
                                           id="rect42373-3"
                                           style="opacity:1;fill:url(#radialGradient8012);fill-opacity:1;stroke:url(#radialGradient44460);stroke-width:0.2807219;stroke-opacity:0.93956042" />
                                        <rect
                                           style="opacity:1;fill:#333333;fill-opacity:1;stroke-width:0.18414214"
                                           id="rect42330-6"
                                           width="33.866665"
                                           height="32.808319"
                                           x="16.933332"
                                           y="263.13333"
                                           rx="3.532774"
                                           ry="3.8749981" />
                                        <rect
                                           style="opacity:1;fill:#b3b3b3;stroke-width:0.20132458"
                                           id="rect42330-3-2"
                                           width="32.49369"
                                           height="32.808334"
                                           x="17.619818"
                                           y="263.13333"
                                           rx="3.3895538"
                                           ry="3.9999995" />
                                        <rect
                                           style="opacity:1;fill:#ececec;stroke-width:0.1921802"
                                           id="rect42330-3-2-2"
                                           width="31.114475"
                                           height="31.220833"
                                           x="18.186256"
                                           y="263.87045"
                                           rx="3.245682"
                                           ry="3.8064513" />
                                        <rect
                                           transform="scale(-1)"
                                           ry="1.6520737"
                                           rx="3.0629039"
                                           y="-293.15945"
                                           x="-48.481586"
                                           height="13.550447"
                                           width="29.362278"
                                           id="rect42330-3-2-2-3"
                                           style="opacity:1;fill:url(#linearGradient47119);fill-opacity:1;stroke-width:0.12299201" />
                                        <rect
                                           style="opacity:1;fill:url(#linearGradient47119-6);fill-opacity:1;stroke-width:0.12298982"
                                           id="rect42330-3-2-2-3-2"
                                           width="29.361433"
                                           height="13.550358"
                                           x="17.203831"
                                           y="265.68738"
                                           rx="3.0628154"
                                           ry="1.6520625"
                                           transform="matrix(0.99996098,-0.00883377,0.00688345,0.99997631,0,0)" />
                                      </g>
                                    </svg>
                                            """
                               }

    roundedbuttonstatesdict = {
                            'On': """
                                    <svg
                                       xmlns:osb="http://www.openswatchbook.org/uri/2009/osb"
                                       xmlns:dc="http://purl.org/dc/elements/1.1/"
                                       xmlns:cc="http://creativecommons.org/ns#"
                                       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                                       xmlns:svg="http://www.w3.org/2000/svg"
                                       xmlns="http://www.w3.org/2000/svg"
                                       xmlns:xlink="http://www.w3.org/1999/xlink"
                                       xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
                                       xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
                                       width="256"
                                       height="129"
                                       viewBox="0 0 67.73248 34.13082"
                                       version="1.1"
                                       id="svg8"
                                       inkscape:version="0.92.1 unknown"
                                       sodipodi:docname="RoundedOnButton.svg">
                                      <defs
                                         id="defs2">
                                        <linearGradient
                                           id="linearGradient46973"
                                           osb:paint="gradient">
                                          <stop
                                             style="stop-color:#000000;stop-opacity:1;"
                                             offset="0"
                                             id="stop46969" />
                                          <stop
                                             style="stop-color:#000000;stop-opacity:0;"
                                             offset="1"
                                             id="stop46971" />
                                        </linearGradient>
                                        <linearGradient
                                           id="linearGradient46862"
                                           osb:paint="solid">
                                          <stop
                                             style="stop-color:#ececec;stop-opacity:1;"
                                             offset="0"
                                             id="stop46860" />
                                        </linearGradient>
                                        <linearGradient
                                           inkscape:collect="always"
                                           id="linearGradient47117">
                                          <stop
                                             style="stop-color:#cccccc;stop-opacity:1;"
                                             offset="0"
                                             id="stop47113" />
                                          <stop
                                             style="stop-color:#cccccc;stop-opacity:0;"
                                             offset="1"
                                             id="stop47115" />
                                        </linearGradient>
                                        <radialGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient4625"
                                           id="radialGradient4627"
                                           cx="23.017721"
                                           cy="353.20093"
                                           fx="23.017721"
                                           fy="353.20093"
                                           r="33.071648"
                                           gradientTransform="matrix(0.9999664,0.00819926,-0.00407819,0.49736889,12.288994,103.71222)"
                                           gradientUnits="userSpaceOnUse" />
                                        <linearGradient
                                           inkscape:collect="always"
                                           id="linearGradient4625">
                                          <stop
                                             style="stop-color:#99ff55;stop-opacity:1;"
                                             offset="0"
                                             id="stop4621" />
                                          <stop
                                             style="stop-color:#99ff55;stop-opacity:0;"
                                             offset="1"
                                             id="stop4623" />
                                        </linearGradient>
                                        <radialGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient4617"
                                           id="radialGradient44460-2"
                                           cx="27.781246"
                                           cy="262.60416"
                                           fx="27.781246"
                                           fy="262.60416"
                                           r="33.337498"
                                           gradientTransform="matrix(1.7352948,0.01419348,-0.00404564,0.49340262,-13.280736,149.60821)"
                                           gradientUnits="userSpaceOnUse" />
                                        <linearGradient
                                           inkscape:collect="always"
                                           id="linearGradient4617">
                                          <stop
                                             style="stop-color:#66ff00;stop-opacity:1;"
                                             offset="0"
                                             id="stop4613" />
                                          <stop
                                             style="stop-color:#66ff00;stop-opacity:0;"
                                             offset="1"
                                             id="stop4615" />
                                        </linearGradient>
                                        <linearGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="linearGradient47119-6-3"
                                           x1="41.2561"
                                           y1="248.90253"
                                           x2="41.214836"
                                           y2="256.65088"
                                           gradientUnits="userSpaceOnUse"
                                           gradientTransform="matrix(0.8973486,0,0,0.99798919,10.922592,17.782479)" />
                                        <linearGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="linearGradient47119-5-9"
                                           x1="41.2561"
                                           y1="248.90253"
                                           x2="41.067112"
                                           y2="255.32812"
                                           gradientUnits="userSpaceOnUse"
                                           gradientTransform="matrix(0.89737575,0,0,0.99799499,-88.935714,-541.14419)" />
                                      </defs>
                                      <sodipodi:namedview
                                         id="base"
                                         pagecolor="#ffffff"
                                         bordercolor="#666666"
                                         borderopacity="1.0"
                                         inkscape:pageopacity="0.0"
                                         inkscape:pageshadow="2"
                                         inkscape:zoom="0.49497475"
                                         inkscape:cx="-771.7445"
                                         inkscape:cy="10.192956"
                                         inkscape:document-units="px"
                                         inkscape:current-layer="layer1"
                                         showgrid="false"
                                         units="px"
                                         inkscape:window-width="1916"
                                         inkscape:window-height="1057"
                                         inkscape:window-x="5760"
                                         inkscape:window-y="0"
                                         inkscape:window-maximized="0"
                                         scale-x="0.26458" />
                                      <metadata
                                         id="metadata5">
                                        <rdf:RDF>
                                          <cc:Work
                                             rdf:about="">
                                            <dc:format>image/svg+xml</dc:format>
                                            <dc:type
                                               rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
                                            <dc:title />
                                          </cc:Work>
                                        </rdf:RDF>
                                      </metadata>
                                      <g
                                         inkscape:label="Layer 1"
                                         inkscape:groupmode="layer"
                                         id="layer1"
                                         transform="translate(0,-262.86875)">
                                        <rect
                                           style="opacity:1;fill:#666666;stroke-width:0.26431346"
                                           id="rect42330-9"
                                           width="67.731026"
                                           height="33.798767"
                                           x="0"
                                           y="263.20081"
                                           rx="13.229"
                                           ry="13.229" />
                                        <rect
                                           style="opacity:1;fill:#b3b3b3;stroke-width:0.29037237"
                                           id="rect42330-3-1"
                                           width="67.731026"
                                           height="32.74255"
                                           x="0"
                                           y="263.20081"
                                           rx="13.229"
                                           ry="13.229" />
                                        <rect
                                           ry="13.229"
                                           rx="13.229"
                                           y="263.99298"
                                           x="0.79373169"
                                           height="31.158237"
                                           width="66.143578"
                                           id="rect42373-2"
                                           style="opacity:1;fill:#00aa00;fill-opacity:1;stroke-width:0.27992097" />
                                        <rect
                                           ry="13.229"
                                           rx="13.229"
                                           y="263.86902"
                                           x="0.93408203"
                                           height="31.406181"
                                           width="65.862862"
                                           id="rect42373-3-7"
                                           style="opacity:1;fill:url(#radialGradient4627);fill-opacity:1;stroke:url(#radialGradient44460-2);stroke-width:0.28043568;stroke-opacity:0.93956042" />
                                        <rect
                                           style="opacity:1;fill:#0c5a00;fill-opacity:1;stroke-width:0.18395628"
                                           id="rect42330-6-0"
                                           width="33.866241"
                                           height="32.742535"
                                           x="33.621399"
                                           y="263.13336"
                                           rx="13.229"
                                           ry="13.229" />
                                        <rect
                                           style="opacity:1;fill:#b3b3b3;stroke-width:0.20278068"
                                           id="rect42330-3-2-9"
                                           width="33.031647"
                                           height="32.74255"
                                           x="34.455994"
                                           y="263.13333"
                                           rx="13.229"
                                           ry="13.229" />
                                        <rect
                                           style="opacity:1;fill:#ececec;stroke-width:0.19357017"
                                           id="rect42330-3-2-2-36"
                                           width="31.629591"
                                           height="31.158237"
                                           x="35.031769"
                                           y="263.86902"
                                           rx="13.229"
                                           ry="13.229" />
                                        <rect
                                           transform="scale(-1)"
                                           ry="13.229"
                                           rx="13.229"
                                           y="-293.09921"
                                           x="-65.828644"
                                           height="13.52328"
                                           width="29.848389"
                                           id="rect42330-3-2-2-3-0"
                                           style="opacity:1;fill:url(#linearGradient47119-5-9);fill-opacity:1;stroke-width:0.12388157" />
                                        <rect
                                           style="opacity:1;fill:url(#linearGradient47119-6-3);fill-opacity:1;stroke-width:0.12387931"
                                           id="rect42330-3-2-2-3-2-6"
                                           width="29.847486"
                                           height="13.523202"
                                           x="34.028969"
                                           y="265.82593"
                                           rx="13.229"
                                           ry="13.229"
                                           transform="matrix(0.99996239,-0.00867248,0.00701146,0.99997542,0,0)" />
                                      </g>
                                    </svg>
                                    """,
                            'Off': """
                                   <svg
                                       xmlns:osb="http://www.openswatchbook.org/uri/2009/osb"
                                       xmlns:dc="http://purl.org/dc/elements/1.1/"
                                       xmlns:cc="http://creativecommons.org/ns#"
                                       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                                       xmlns:svg="http://www.w3.org/2000/svg"
                                       xmlns="http://www.w3.org/2000/svg"
                                       xmlns:xlink="http://www.w3.org/1999/xlink"
                                       xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
                                       xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
                                       width="256"
                                       height="129"
                                       viewBox="0 0 67.73248 34.13082"
                                       version="1.1"
                                       id="svg8"
                                       inkscape:version="0.92.1 unknown"
                                       sodipodi:docname="RoundedOffButton.svg">
                                      <defs
                                         id="defs2">
                                        <linearGradient
                                           inkscape:collect="always"
                                           id="7812">
                                          <stop
                                             style="stop-color:#005000;stop-opacity:1;"
                                             offset="0"
                                             id="stop7933" />
                                          <stop
                                             style="stop-color:#005000;stop-opacity:0;"
                                             offset="1"
                                             id="stop7935" />
                                        </linearGradient>
                                        <linearGradient
                                           id="linearGradient46973"
                                           osb:paint="gradient">
                                          <stop
                                             style="stop-color:#000000;stop-opacity:1;"
                                             offset="0"
                                             id="stop46969" />
                                          <stop
                                             style="stop-color:#000000;stop-opacity:0;"
                                             offset="1"
                                             id="stop46971" />
                                        </linearGradient>
                                        <linearGradient
                                           id="linearGradient46862"
                                           osb:paint="solid">
                                          <stop
                                             style="stop-color:#ececec;stop-opacity:1;"
                                             offset="0"
                                             id="stop46860" />
                                        </linearGradient>
                                        <linearGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="linearGradient47119-6-1"
                                           x1="41.2561"
                                           y1="248.90253"
                                           x2="41.214836"
                                           y2="256.65088"
                                           gradientUnits="userSpaceOnUse"
                                           gradientTransform="matrix(0.89734881,5.4897511e-8,-4.4871239e-8,0.99998121,-23.246377,17.159312)" />
                                        <linearGradient
                                           inkscape:collect="always"
                                           id="linearGradient47117">
                                          <stop
                                             style="stop-color:#cccccc;stop-opacity:1;"
                                             offset="0"
                                             id="stop47113" />
                                          <stop
                                             style="stop-color:#cccccc;stop-opacity:0;"
                                             offset="1"
                                             id="stop47115" />
                                        </linearGradient>
                                        <linearGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="linearGradient47119-3"
                                           x1="41.2561"
                                           y1="248.90253"
                                           x2="41.067112"
                                           y2="255.32812"
                                           gradientUnits="userSpaceOnUse"
                                           gradientTransform="matrix(0.8973758,0,0,0.99998712,-54.763421,-541.86262)" />
                                        <linearGradient
                                           inkscape:collect="always"
                                           id="7744">
                                          <stop
                                             style="stop-color:#005000;stop-opacity:1;"
                                             offset="0"
                                             id="stop44454" />
                                          <stop
                                             style="stop-color:#0caa00;stop-opacity:0"
                                             offset="1"
                                             id="stop44456" />
                                        </linearGradient>
                                        <radialGradient
                                           inkscape:collect="always"
                                           xlink:href="#7744"
                                           id="radialGradient7910"
                                           cx="27.780457"
                                           cy="279.53751"
                                           fx="27.780457"
                                           fy="279.53751"
                                           r="33.072918"
                                           gradientTransform="matrix(1.0605954,0,0,0.43150718,4.401612,158.91485)"
                                           gradientUnits="userSpaceOnUse" />
                                        <radialGradient
                                           inkscape:collect="always"
                                           xlink:href="#7812"
                                           id="radialGradient7939"
                                           cx="27.780457"
                                           cy="279.53751"
                                           fx="27.780457"
                                           fy="279.53751"
                                           r="32.932556"
                                           gradientTransform="matrix(0.9999871,0,0,0.47777758,6.0853402,145.98054)"
                                           gradientUnits="userSpaceOnUse" />
                                      </defs>
                                      <sodipodi:namedview
                                         id="base"
                                         pagecolor="#ffffff"
                                         bordercolor="#666666"
                                         borderopacity="1.0"
                                         inkscape:pageopacity="0.0"
                                         inkscape:pageshadow="2"
                                         inkscape:zoom="1.4"
                                         inkscape:cx="-185.38798"
                                         inkscape:cy="-6.8966862"
                                         inkscape:document-units="px"
                                         inkscape:current-layer="layer1"
                                         showgrid="false"
                                         units="px"
                                         inkscape:window-width="1916"
                                         inkscape:window-height="1057"
                                         inkscape:window-x="5760"
                                         inkscape:window-y="1080"
                                         inkscape:window-maximized="0" />
                                      <metadata
                                         id="metadata5">
                                        <rdf:RDF>
                                          <cc:Work
                                             rdf:about="">
                                            <dc:format>image/svg+xml</dc:format>
                                            <dc:type
                                               rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
                                            <dc:title />
                                          </cc:Work>
                                        </rdf:RDF>
                                      </metadata>
                                      <g
                                         inkscape:label="Layer 1"
                                         inkscape:groupmode="layer"
                                         id="layer1"
                                         transform="translate(0,-262.86875)">
                                        <rect
                                           style="opacity:1;fill:#666666;stroke-width:0.26458001"
                                           id="rect42330-4"
                                           width="67.732475"
                                           height="33.866241"
                                           x="9.5439134e-07"
                                           y="263.13333"
                                           ry="13.228996"
                                           rx="13.228996" />
                                        <rect
                                           style="opacity:1;fill:#b3b3b3;stroke-width:0.29066515"
                                           id="rect42330-3-5"
                                           width="67.732475"
                                           height="32.807911"
                                           x="9.5439134e-07"
                                           y="263.13333"
                                           ry="13.228996"
                                           rx="13.228996" />
                                        <rect
                                           y="263.92709"
                                           x="0.79375291"
                                           height="31.220432"
                                           width="66.144981"
                                           id="rect42373-0"
                                           style="opacity:1;fill:#112b0b;fill-opacity:1;stroke-width:0.28020319"
                                           ry="13.228996"
                                           rx="13.228996" />
                                        <rect
                                           y="263.80286"
                                           x="0.93330657"
                                           height="31.468872"
                                           width="65.864265"
                                           id="rect42373-3-3"
                                           style="opacity:1;fill:url(#radialGradient7910);fill-opacity:1;stroke:url(#radialGradient7939);stroke-width:0;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
                                           ry="13.228996"
                                           rx="13.228996" />
                                        <rect
                                           style="opacity:1;fill:#2d0000;fill-opacity:1;stroke-width:0.18413982"
                                           id="rect42330-6-6"
                                           width="33.866241"
                                           height="32.807896"
                                           x="-33.866241"
                                           y="-295.94122"
                                           transform="scale(-1)"
                                           ry="13.228996"
                                           rx="11.683769" />
                                        <rect
                                           style="opacity:1;fill:#b3b3b3;stroke-width:0.20298296"
                                           id="rect42330-3-2-1"
                                           width="33.031651"
                                           height="32.807911"
                                           x="-33.031662"
                                           y="-295.94125"
                                           transform="scale(-1)"
                                           ry="13.228996"
                                           rx="11.683769" />
                                        <rect
                                           style="opacity:1;fill:#ececec;stroke-width:0.19376327"
                                           id="rect42330-3-2-2-0"
                                           width="31.629597"
                                           height="31.220432"
                                           x="-32.455887"
                                           y="-295.20413"
                                           transform="scale(-1)"
                                           ry="13.228996"
                                           rx="11.683769" />
                                        <rect
                                           transform="scale(-1)"
                                           y="-293.32248"
                                           x="-31.656364"
                                           height="13.550274"
                                           width="29.848396"
                                           id="rect42330-3-2-2-3-3"
                                           style="opacity:1;fill:url(#linearGradient47119-3);fill-opacity:1;stroke-width:0.12400515"
                                           ry="13.228996"
                                           rx="11.683769" />
                                        <rect
                                           style="opacity:1;fill:url(#linearGradient47119-6-1);fill-opacity:1;stroke-width:0.1240029"
                                           id="rect42330-3-2-2-3-2-2"
                                           width="29.847494"
                                           height="13.550194"
                                           x="-0.13999988"
                                           y="265.69797"
                                           transform="matrix(0.99996224,-0.0086898,0.0069975,0.99997552,0,0)"
                                           ry="13.228905"
                                           rx="11.683867" />
                                      </g>
                                    </svg>
                                   """,
                            'Disconnected': """
                                    <svg
                                       xmlns:dc="http://purl.org/dc/elements/1.1/"
                                       xmlns:cc="http://creativecommons.org/ns#"
                                       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                                       xmlns:svg="http://www.w3.org/2000/svg"
                                       xmlns="http://www.w3.org/2000/svg"
                                       xmlns:xlink="http://www.w3.org/1999/xlink"
                                       xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
                                       xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
                                       width="256"
                                       height="129"
                                       viewBox="0 0 67.733331 34.131251"
                                       version="1.1"
                                       id="svg159"
                                       inkscape:version="0.92.1 unknown"
                                       sodipodi:docname="RoundedDisconnectButton.svg">
                                      <defs
                                         id="defs153">
                                        <linearGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="linearGradient47119-6-7"
                                           x1="41.2561"
                                           y1="248.90253"
                                           x2="41.214836"
                                           y2="256.65088"
                                           gradientUnits="userSpaceOnUse"
                                           gradientTransform="matrix(0.88273561,2.0057873e-8,-1.4941557e-8,0.99999332,-5.5335438,18.204087)" />
                                        <linearGradient
                                           inkscape:collect="always"
                                           id="linearGradient47117">
                                          <stop
                                             style="stop-color:#cccccc;stop-opacity:1;"
                                             offset="0"
                                             id="stop47113" />
                                          <stop
                                             style="stop-color:#cccccc;stop-opacity:0;"
                                             offset="1"
                                             id="stop47115" />
                                        </linearGradient>
                                        <linearGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="linearGradient1689"
                                           gradientUnits="userSpaceOnUse"
                                           gradientTransform="matrix(0.88276109,0,0,0.99999997,-71.212307,-541.17351)"
                                           x1="41.2561"
                                           y1="248.90253"
                                           x2="41.067112"
                                           y2="255.32812" />
                                        <radialGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="radialGradient44460-5"
                                           cx="27.781246"
                                           cy="262.60416"
                                           fx="27.781246"
                                           fy="262.60416"
                                           r="33.337498"
                                           gradientTransform="matrix(1.1815126,-0.01290238,0.00424111,0.38837207,-0.07175464,177.9078)"
                                           gradientUnits="userSpaceOnUse" />
                                        <radialGradient
                                           inkscape:collect="always"
                                           xlink:href="#linearGradient47117"
                                           id="radialGradient8020"
                                           cx="33.865868"
                                           cy="279.53745"
                                           fx="33.865868"
                                           fy="279.53748"
                                           r="33.072918"
                                           gradientTransform="matrix(1.1909647,-0.01300556,0.00427502,0.39147863,-7.6622104,170.54499)"
                                           gradientUnits="userSpaceOnUse" />
                                      </defs>
                                      <sodipodi:namedview
                                         id="base"
                                         pagecolor="#ffffff"
                                         bordercolor="#666666"
                                         borderopacity="1.0"
                                         inkscape:pageopacity="0.0"
                                         inkscape:pageshadow="2"
                                         inkscape:zoom="1.7167969"
                                         inkscape:cx="-61.7611"
                                         inkscape:cy="-30.019748"
                                         inkscape:document-units="px"
                                         inkscape:current-layer="layer1"
                                         showgrid="false"
                                         units="px"
                                         inkscape:window-width="1916"
                                         inkscape:window-height="1057"
                                         inkscape:window-x="3840"
                                         inkscape:window-y="1080"
                                         inkscape:window-maximized="0"
                                         inkscape:measure-start="0,0"
                                         inkscape:measure-end="0,0" />
                                      <metadata
                                         id="metadata156">
                                        <rdf:RDF>
                                          <cc:Work
                                             rdf:about="">
                                            <dc:format>image/svg+xml</dc:format>
                                            <dc:type
                                               rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
                                            <dc:title />
                                          </cc:Work>
                                        </rdf:RDF>
                                      </metadata>
                                      <g
                                         inkscape:label="Layer 1"
                                         inkscape:groupmode="layer"
                                         id="layer1"
                                         transform="translate(0,-262.86873)">
                                        <rect
                                           style="opacity:1;fill:#666666;stroke-width:0.26458332"
                                           id="rect42330-9"
                                           width="67.73333"
                                           height="33.866665"
                                           x="0"
                                           y="263.1333"
                                           rx="13.229167"
                                           ry="13.229167" />
                                        <rect
                                           style="opacity:1;fill:#b3b3b3;stroke-width:0.2906689"
                                           id="rect42330-3-1"
                                           width="67.73333"
                                           height="32.808334"
                                           x="0"
                                           y="263.1333"
                                           rx="13.229167"
                                           ry="13.229167" />
                                        <rect
                                           ry="13.229167"
                                           rx="13.229167"
                                           y="263.92706"
                                           x="0.79370117"
                                           height="31.220833"
                                           width="66.145836"
                                           id="rect42373-2"
                                           style="opacity:1;fill:#333333;fill-opacity:1;stroke-width:0.28020677" />
                                        <rect
                                           ry="13.229167"
                                           rx="13.229167"
                                           y="263.80286"
                                           x="0.9333176"
                                           height="31.469278"
                                           width="65.865112"
                                           id="rect42373-3-7"
                                           style="opacity:1;fill:url(#radialGradient8020);fill-opacity:1;stroke:url(#radialGradient44460-5);stroke-width:0.2807219;stroke-opacity:0.93956042" />
                                        <rect
                                           style="opacity:1;fill:#333333;fill-opacity:1;stroke-width:0.18414214"
                                           id="rect42330-6-0"
                                           width="33.866665"
                                           height="32.808319"
                                           x="16.933332"
                                           y="263.13333"
                                           rx="11.441442"
                                           ry="13.229167" />
                                        <rect
                                           style="opacity:1;fill:#b3b3b3;stroke-width:0.20132458"
                                           id="rect42330-3-2-3"
                                           width="32.493694"
                                           height="32.808334"
                                           x="17.619816"
                                           y="263.1333"
                                           rx="11.441442"
                                           ry="13.229167" />
                                        <rect
                                           style="opacity:1;fill:#ececec;stroke-width:0.1921802"
                                           id="rect42330-3-2-2-6"
                                           width="31.114475"
                                           height="31.220833"
                                           x="18.186249"
                                           y="263.87042"
                                           rx="11.441442"
                                           ry="13.229167" />
                                        <rect
                                           transform="scale(-1)"
                                           ry="13.229167"
                                           rx="11.441442"
                                           y="-292.63028"
                                           x="-48.48159"
                                           height="13.550447"
                                           width="29.362278"
                                           id="rect42330-3-2-2-3-0"
                                           style="opacity:1;fill:url(#linearGradient1689);fill-opacity:1;stroke-width:0.12299201" />
                                        <rect
                                           style="opacity:1;fill:url(#linearGradient47119-6-7);fill-opacity:1;stroke-width:0.12298982"
                                           id="rect42330-3-2-2-3-2-6"
                                           width="29.361429"
                                           height="13.550358"
                                           x="17.196539"
                                           y="266.74576"
                                           rx="11.441554"
                                           ry="13.229061"
                                           transform="matrix(0.99996098,-0.00883377,0.00688345,0.99997631,0,0)" />
                                      </g>
                                    </svg>
                                    """
                               }

    def __init__(self, parent=None, init_channel=None):
        """Initialize all internal states and properties."""
        QAbstractButton.__init__(self, parent)
        PyDMWritableWidget.__init__(self, init_channel=init_channel)
        self._bit = -1
        self.value = 0
        self.clicked.connect(self.send_value)
        self.shape = 0
        self.renderer = QSvgRenderer()
        self.setCheckable(True)

    def value_changed(self, new_val):
        """
        Callback invoked when the Channel value is changed.

        Display the value of new_val accordingly. If :attr:'pvBit' is n>=0 or
        positive the button display the state of the n-th digit of the channel.

        Parameters
        ----------
        new_value : str, int, float, bool or np.ndarray
            The new value from the channel. The type depends on the channel.
        """
        super(PyDMStateButton, self).value_changed(new_val)
        value = int(new_val)
        if self._bit >= 0:
            value = (value >> self._bit) & 1
        if value:
            self.setChecked(True)
        else:
            self.setChecked(False)
        self.update()

    def send_value(self, checked):
        """
        Emit a :attr:`send_value_signal` to update channel value.

        If :attr:'pvBit' is n>=0 or positive the button toggles the state of
        the n-th digit of the channel. Otherwise it toggles the whole value.
        """
        val = 1 if checked else 0
        if self._bit >= 0:
            val = int(self.value)
            val ^= (-checked ^ val) & (1 << self._bit)
            # For explanation look:
            # https://stackoverflow.com/questions/47981/how-do-you-set-clear-and-toggle-a-single-bit
        self.send_value_signal[self.channeltype].emit(self.channeltype(val))

    def sizeHint(self):
        """Return size hint to define size on initialization."""
        return QSize(72, 36)

    def paintEvent(self, event):
        """Treat appearence changes based on connection state and value."""
        if self._connected is False:
            state = 'Disconnected'
        elif self.value == 1:
            state = 'On'
        elif self.value == 0:
            state = 'Off'

        if self.shape == 0:
            shape_dict = PyDMStateButton.squaredbuttonstatesdict
        elif self.shape == 1:
            shape_dict = PyDMStateButton.roundedbuttonstatesdict

        option = QStyleOption()
        option.initFrom(self)
        h = option.rect.height()
        w = option.rect.width()
        aspect = 2.0
        ah = w/aspect
        aw = w
        if ah > h:
            ah = h
            aw = h*aspect
        x = abs(aw-w)/2.0
        y = abs(ah-h)/2.0
        bounds = QRectF(x, y, aw, ah)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        shape_str = shape_dict[state]
        buttonstate_bytearray = bytes(shape_str, 'utf-8')
        self.renderer.load(QByteArray(buttonstate_bytearray))
        self.renderer.render(painter, bounds)

    @pyqtProperty(buttonShapeMap)
    def shape(self):
        """
        Property to define the shape of the button.

        Returns
        -------
        int
        """
        return self._shape

    @shape.setter
    def shape(self, new_shape):
        """
        Property to define the shape of the button.

        Parameters
        ----------
        value : int
        """
        self._shape = new_shape
        self.update()

    @pyqtProperty(int)
    def pvbit(self):
        """
        Property to define which PV bit to control.

        Returns
        -------
        int
        """
        return int(self._bit)

    @pvbit.setter
    def pvbit(self, bit):
        """
        Property to define which PV bit to control.

        Parameters
        ----------
        value : int
        """
        if bit >= 0:
            self._bit = int(bit)
