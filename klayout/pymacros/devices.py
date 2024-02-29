<!--
Copyright (C) 2024 Spherical Systems B.V. info@spherical-systems.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

<?xml version="1.0" encoding="utf-8"?>
<klayout-macro>
 <description/>
 <version/>
 <category>pymacros</category>
 <prolog/>
 <epilog/>
 <doc/>
 <autorun>true</autorun>
 <autorun-early>false</autorun-early>
 <priority>0</priority>
 <shortcut/>
 <show-in-menu>false</show-in-menu>
 <group-name/>
 <menu-path/>
 <interpreter>python</interpreter>
 <dsl-interpreter-name/>
 <text>import pya
import math

from pdkmaster.design import library as _lbry
from pdkmaster.design import cell as _cell
from pdkmaster.technology import geometry as _geo
import pdkmaster.pdk_selected as pdk_selected
from pdkmaster.io.klayout import export as _klexp



class Mos(pya.PCellDeclarationHelper):

  def __init__(self):

    # Important: initialize the super class
    super(Mos, self).__init__()
    
    self.device_choices = [("nmos", 0), ("pmos", 1), ("nmos5", 2), ("pmos5", 3)]
  
    self.param("w",  self.TypeDouble, "Width (um)", default = 1)
    self.param("l",  self.TypeDouble, "Length (um)", default = 1)
    self.param("device", self.TypeInt, "Device", choices=self.device_choices, default=0)
    
  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return f"{self.device_choices[int(self.device)][0]} (w={self.w:1.3f}, l={self.l:1.3f})"



  def produce_impl(self):
  
    lib = _lbry.Library(
        name="lib",
        tech=pdk_selected.tech,
    )


    class MosDevice(_cell.OnDemandCell):
      def __init__(self, *, lib: _lbry.Library, name: str,
                        device: str, w: str, l: str):
          super().__init__(name=name, tech=pdk_selected.tech, cktfab=pdk_selected.cktfab, layoutfab=pdk_selected.layoutfab)
          
          self.device = device
          self.w = w
          self.l = l
  
      def _create_circuit(self):
  
          ckt = self.new_circuit()
          
          if self.device == "nmos":
            device_primitive = pdk_selected.tech._primitives.nmos
          elif self.device == "pmos":
            device_primitive = pdk_selected.tech._primitives.pmos
          elif self.device == "nmos5":
            device_primitive = pdk_selected.tech._primitives.nmos5
          elif self.device == "pmos5":
            device_primitive = pdk_selected.tech._primitives.pmos5
          else:
            assert "Unsupported device selected"
          
          mos = ckt.instantiate(device_primitive, name="mos", l=self.l, w=self.w)
          ckt.new_net(name="gate", external=True, childports=mos.ports.gate)
          ckt.new_net(name="source", external=True, childports=mos.ports.sourcedrain1)
          ckt.new_net(name="drain", external=True, childports=mos.ports.sourcedrain2)
          ckt.new_net(name="bulk", external=True, childports=mos.ports.bulk)
  
      def _create_layout(self):
  
          layouter = self.new_circuitlayouter()
          inst = self.circuit.instances[0]
          layouter.place(object_=inst)
          
    mos_device = MosDevice(lib=lib, name="mos", device=self.device_choices[self.device][0], w=self.w, l=self.l)
    lib.cells += mos_device
    
    klay1v8db = _klexp.export2db(
      obj=lib,
      add_pin_label=True,
      gds_layers=pdk_selected.gds_layers,
      cell_name=None,
      merge=True,
    )
    
    cell_klayout = [_ for _ in klay1v8db.each_cell()][0]
    
    layers_valid = klay1v8db.layer_indexes()
    layers_infos = klay1v8db.layer_infos()
    
    for layer in layers_valid:
      layer_nums = pdk_selected.gds_layers[layers_infos[layer].name]
      layer_ref = self.layout.layer(layer_nums[0], layer_nums[1])
      
      for shape in cell_klayout.each_shape(layer):
        self.cell.shapes(layer_ref).insert(shape)



class Via(pya.PCellDeclarationHelper):

  def __init__(self):

    # Important: initialize the super class
    super(Via, self).__init__()
    
    self.via_choices = [("cont_diff_p", 0), ("cont_diff_n", 1), ("cont_poly", 2), ("via1", 3),
                        ("via2", 4), ("via3", 5), ("via4", 6), ("viat5", 7)]
  
    self.param("rows",  self.TypeInt, "Rows", default = 1)
    self.param("columns",  self.TypeInt, "Columns", default = 1)
    self.param("via", self.TypeInt, "Type", choices=self.via_choices, default=0)

    self.param("top_left", self.TypeDouble, "Top Layer - Left Enclosure", default=0)
    self.param("top_right", self.TypeDouble, "Top Layer - Right Enclosure", default=0)
    self.param("top_bottom", self.TypeDouble, "Top Layer - Bottom Enclosure", default=0)
    self.param("top_top", self.TypeDouble, "Top Layer - Top Enclosure", default=0)

    self.param("bot_left", self.TypeDouble, "Bottom Layer - Left Enclosure", default=0)
    self.param("bot_right", self.TypeDouble, "Bottom Layer - Right Enclosure", default=0)
    self.param("bot_bottom", self.TypeDouble, "Bottom Layer - Bottom Enclosure", default=0)
    self.param("bot_top", self.TypeDouble, "Bottom Layer - Top Enclosure", default=0)


    
  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return f"{self.via_choices[int(self.via)][0]} (rows={self.rows}, l={self.columns})"



  def produce_impl(self):
  
    lib = _lbry.Library(
        name="lib",
        tech=pdk_selected.tech,
    )


    class ViaDevice(_cell.OnDemandCell):
      def __init__(self, *, lib: _lbry.Library, name: str,
                        device: str, rows: str, columns: str, top_enclosure: dict, bottom_enclosure: dict):
          super().__init__(name=name, tech=pdk_selected.tech, cktfab=pdk_selected.cktfab, layoutfab=pdk_selected.layoutfab)
          
          self.device = device
          self.rows = rows
          self.columns = columns
          self.top_enclosure = top_enclosure
          self.bottom_enclosure = bottom_enclosure
  
      def _create_circuit(self):
  
          ckt = self.new_circuit()
          ckt.new_net(name="conn", external=True)
  
      def _create_layout(self):
  
          layouter = self.new_circuitlayouter()
          
          ################################################################################
          def via_extent_find(mask_name):
            mask_extent_left   = 0
            mask_extent_bottom = 0
            mask_extent_right  = 0
            mask_extent_top    = 0
            for sublayout in via._sublayouts:
              for shape in sublayout._shapes:
                if shape._mask.name == mask_name:

                  if isinstance(shape._shape, _geo.RepeatedShape):
                    if shape._shape._m_dxy is not None:
                      extra_offset_h = (shape._shape._m_dxy._x-(shape._shape._shape._right-shape._shape._shape._left))/2
                      via_extent_left   = -shape._shape._m*shape._shape._m_dxy._x / 2 + extra_offset_h
                      via_extent_right  =  shape._shape._m*shape._shape._m_dxy._x / 2 - extra_offset_h
                    else:
                      via_extent_left   = shape._shape._shape._left
                      via_extent_right  = shape._shape._shape._right
                    
                    extra_offset_v = (shape._shape._n_dxy._y-(shape._shape._shape._top-shape._shape._shape._bottom))/2
                    via_extent_top    =  shape._shape._n*shape._shape._n_dxy._y / 2 - extra_offset_v
                    via_extent_bottom = -shape._shape._n*shape._shape._n_dxy._y / 2 + extra_offset_v

                  elif isinstance(shape._shape, _geo.Rect):
                    via_extent_left   = shape._shape._left
                    via_extent_bottom = shape._shape._bottom
                    via_extent_right  = shape._shape._right
                    via_extent_top    = shape._shape._top

                  mask_extent_left   = min(mask_extent_left,   via_extent_left)
                  mask_extent_bottom = min(mask_extent_bottom, via_extent_bottom)
                  mask_extent_right  = max(mask_extent_right,  via_extent_right)
                  mask_extent_top    = max(mask_extent_top,    via_extent_top)

            return mask_extent_left, mask_extent_bottom, mask_extent_right, mask_extent_top
          ################################################################################
          def conductor_wire(net, wire, cont, enclosure, implant=None):

            via_extent_left, via_extent_bottom, via_extent_right, via_extent_top = via_extent_find(cont)
            mask_extent_left, mask_extent_bottom, mask_extent_right, mask_extent_top = via_extent_find(wire.name)

            if  (enclosure["left"] != 0) or \
                (enclosure["right"] != 0) or \
                (enclosure["bottom"] != 0) or \
                (enclosure["top"] != 0):

              left_extent   = min(mask_extent_left,   via_extent_left   - enclosure["left"])
              bottom_extent = min(mask_extent_bottom, via_extent_bottom - enclosure["bottom"])
              right_extent  = max(mask_extent_right,  via_extent_right  + enclosure["right"])
              top_extent    = max(mask_extent_top,    via_extent_top    + enclosure["top"])

              shape = _geo.Rect(left   = left_extent,
                                bottom = bottom_extent,
                                right  = right_extent,
                                top    = top_extent)

              if implant is None:
                wire_obj = layouter.add_wire( net=net,
                                              wire=wire,
                                              shape=shape)
                layouter.place(object_=wire_obj)
              else:
                # place diff
                wire_obj = layouter.add_wire( net=net,
                                              wire=wire,
                                              shape=shape)
                layouter.place(object_=wire_obj)

                # figure out implant shape
                implant_extent_left, implant_extent_bottom, implant_extent_right, implant_extent_top = via_extent_find(implant.name)
                delta_extent_left = implant_extent_left - mask_extent_left
                delta_extent_right = implant_extent_right - mask_extent_right
                delta_extent_bottom = implant_extent_bottom - mask_extent_bottom
                delta_extent_top = implant_extent_top - mask_extent_top
                implant_shape = _geo.Rect(left   = left_extent + delta_extent_left,
                                          bottom = bottom_extent + delta_extent_bottom,
                                          right  = right_extent + delta_extent_right,
                                          top    = top_extent + delta_extent_top)
                layouter.layout.add_shape(net=net,
                                          layer=implant,
                                          shape=implant_shape)


          ################################################################################

          setup = {
            "cont_diff_p" : {"net"            : self.circuit.nets.conn,
                             "wire"           : pdk_selected.tech._primitives.cont,
                             "bottom"         : pdk_selected.tech._primitives.diff,
                             "bottom_implant" : pdk_selected.tech._primitives.pimp,
                             "cont"           : pdk_selected.tech._primitives.cont,
                             "bottom_layer"   : pdk_selected.tech._primitives.diff,
                             "top_layer"      : pdk_selected.tech._primitives.met1},
            "cont_diff_n" : {"net"            : self.circuit.nets.conn,
                             "wire"           : pdk_selected.tech._primitives.cont,
                             "bottom"         : pdk_selected.tech._primitives.diff,
                             "bottom_implant" : pdk_selected.tech._primitives.nimp,
                             "cont"           : pdk_selected.tech._primitives.cont,
                             "bottom_layer"   : pdk_selected.tech._primitives.diff,
                             "top_layer"      : pdk_selected.tech._primitives.met1},
            "cont_poly"   : {"net"            : self.circuit.nets.conn,
                             "wire"           : pdk_selected.tech._primitives.cont,
                             "bottom"         : pdk_selected.tech._primitives.poly,
                             "cont"           : pdk_selected.tech._primitives.cont,
                             "bottom_layer"   : pdk_selected.tech._primitives.poly,
                             "top_layer"      : pdk_selected.tech._primitives.met1},
            "via1"        : {"net"            : self.circuit.nets.conn,
                             "wire"           : pdk_selected.tech._primitives.via1,
                             "cont"           : pdk_selected.tech._primitives.via1,
                             "bottom_layer"   : pdk_selected.tech._primitives.met1,
                             "top_layer"      : pdk_selected.tech._primitives.met2},
            "via2"        : {"net"            : self.circuit.nets.conn,
                             "wire"           : pdk_selected.tech._primitives.via2,
                             "cont"           : pdk_selected.tech._primitives.via2,
                             "bottom_layer"   : pdk_selected.tech._primitives.met2,
                             "top_layer"      : pdk_selected.tech._primitives.met3},
            "via3"        : {"net"            : self.circuit.nets.conn,
                             "wire"           : pdk_selected.tech._primitives.via3,
                             "cont"           : pdk_selected.tech._primitives.via3,
                             "bottom_layer"   : pdk_selected.tech._primitives.met3,
                             "top_layer"      : pdk_selected.tech._primitives.met4},
            "via4"       : {"net"             : self.circuit.nets.conn,
                             "wire"           : pdk_selected.tech._primitives.via4,
                             "cont"           : pdk_selected.tech._primitives.via4,
                             "bottom_layer"   : pdk_selected.tech._primitives.met4,
                             "top_layer"      : pdk_selected.tech._primitives.met5},
            "via5"       : {"net"             : self.circuit.nets.conn,
                             "wire"           : pdk_selected.tech._primitives.via5,
                             "cont"           : pdk_selected.tech._primitives.via5,
                             "bottom_layer"   : pdk_selected.tech._primitives.met5,
                             "top_layer"      : pdk_selected.tech._primitives.met6},
          }

          for name, setup_i in setup.items():
            if self.device == name:
              setup_i_mod = setup_i.copy()
              del setup_i_mod["cont"]
              del setup_i_mod["top_layer"]
              del setup_i_mod["bottom_layer"]
              setup_i_mod["rows"] = self.rows
              setup_i_mod["columns"] = self.columns
              via = layouter.add_wire(**setup_i_mod)
              layouter.place(object_=via)

              conductor_wire( net       = setup_i["net"],
                              wire      = setup_i["top_layer"],
                              cont      = setup_i["cont"].name,
                              enclosure = self.top_enclosure)

              conductor_wire( net       = setup_i["net"],
                              wire      = setup_i["bottom_layer"],
                              cont      = setup_i["cont"].name,
                              enclosure = self.bottom_enclosure,
                              implant   = setup_i.get("bottom_implant",None))
              return
          
    top_enclosure    = {"left": self.top_left, "right": self.top_right, "bottom": self.top_bottom, "top": self.top_top}
    bottom_enclosure = {"left": self.bot_left, "right": self.bot_right, "bottom": self.bot_bottom, "top": self.bot_top}

    via_device = ViaDevice( lib=lib,
                            name="via",
                            device=self.via_choices[self.via][0],
                            rows=self.rows,
                            columns=self.columns,
                            top_enclosure=top_enclosure,
                            bottom_enclosure=bottom_enclosure)
    lib.cells += via_device
    
    klay1v8db = _klexp.export2db(
      obj=lib,
      add_pin_label=True,
      gds_layers=pdk_selected.gds_layers,
      cell_name=None,
      merge=True,
    )
    
    cell_klayout = [_ for _ in klay1v8db.each_cell()][0]
    
    layers_valid = klay1v8db.layer_indexes()
    layers_infos = klay1v8db.layer_infos()
    
    for layer in layers_valid:
      layer_nums = pdk_selected.gds_layers[layers_infos[layer].name]
      layer_ref = self.layout.layer(layer_nums[0], layer_nums[1])
      
      for shape in cell_klayout.each_shape(layer):
        self.cell.shapes(layer_ref).insert(shape)
    


# The PCell library declaration
# A PCell library must be declared by deriving a custom class from RBA::Library.
# The main purpose of this class is to provide the PCell declarations and to register itself
# with a proper name.
class PCell(pya.Library):

  def __init__(self):
  
    self.description = "PDK Master PCell Set"
    
    # register the PCell declarations
    self.layout().register_pcell("mos", Mos())
    self.layout().register_pcell("via", Via())
    
    # register our library with a name
    self.register("pdkmaster")
    
# instantiate and register the library
PCellPdkMaster()

</text>
</klayout-macro>
