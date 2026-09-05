# Third-party notices

No upstream source is copied in Phase 00. If a later phase distributes or derives from a component, retain its notices and attribution under the recorded license.

| Component | Pinned identity | License | Use/provenance |
|---|---|---|---|
| Klipper and Klipper docs | `f0892d82b0f1c1228454f09eb508eddde2250f4b` | GPL-3.0 | command/architecture reference; no copied code |
| Moonraker and API docs | `985c1d0bbeb90bc057d34a232c9dc3b05e0c6c8d` | GPL-3.0 | API reference; no copied code |
| Cartographer docs | `b0519c0f35ee3d77d7c4b7c16f414ad2e68f559a` | GPL-3.0 | Touch reference; no copied code |
| OpenCV docs/source identity | tag `4.12.0`, deref `49486f61fb25722cbcf586b7f4320921d46fb38e` | Apache-2.0 | candidate CV reference; no copied code |
| kTAMV | `72421f2d54da0de8701c4f84449c6e6b7d060301` | GPL-3.0 | behavioral comparison/evidence provenance |
| KTC | `b880e37a960c4746a370b7f6ac76a6a829430387` | GPL-3.0 | candidate adapter comparison |
| klipper-toolchanger | `94756dfde9b729fd69f9b8780067821c5c99a528` | GPL-3.0 | candidate adapter comparison |

Before release, add copyright holders, exact URLs, modifications, full license texts, and dependency notices for any actually distributed material. Hardware compatibility remains `REQUIRES_HIL`.
## opencv-python-headless 4.14.0.94

Used only by the host-side `vision/jpeg_adapter.py` for bounded JPEG decode and image analysis. The Python wrapper is MIT-licensed; OpenCV is Apache-2.0. Bundled third-party notices remain applicable. No upstream implementation is copied.
