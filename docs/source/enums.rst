.. index:: ! Enumerations

.. role:: val(code)
  :class: enum-val

Enumerations
############

Product Group Device
********************

.. list-table::
  :header-rows: 1
  :widths: 1 4
  :class: first-col-right

  + - Value (:term:`uint16 <int>`)
    - Description

  + - :val:`0x0000`
    - :enum:`SPIKE™ Prime`

Color
*****

.. list-table::
  :header-rows: 1
  :widths: 1 4
  :class: first-col-right

  + - Value (:term:`int8 <int>`)
    - Description

  + - :val:`0x00`
    - :enum:`Black`

  + - :val:`0x01`
    - :enum:`Magenta`

  + - :val:`0x02`
    - :enum:`Purple`

  + - :val:`0x03`
    - :enum:`Blue`

  + - :val:`0x04`
    - :enum:`Azure`

  + - :val:`0x05`
    - :enum:`Turquoise`

  + - :val:`0x06`
    - :enum:`Green`

  + - :val:`0x07`
    - :enum:`Yellow`

  + - :val:`0x08`
    - :enum:`Orange`

  + - :val:`0x09`
    - :enum:`Red`

  + - :val:`0x0A`
    - :enum:`White`

  + - :val:`0xFF`
    - :enum:`Unknown` or no color detected


Hub Port
********

.. list-table::
  :header-rows: 1
  :widths: 1 4
  :class: first-col-right

  + - Value (:term:`uint8 <int>`)
    - Description

  + - :val:`0x00`
    - :enum:`A`

  + - :val:`0x01`
    - :enum:`B`

  + - :val:`0x02`
    - :enum:`C`

  + - :val:`0x03`
    - :enum:`D`

  + - :val:`0x04`
    - :enum:`E`

  + - :val:`0x05`
    - :enum:`F`


Hub Face
********

.. list-table::
  :header-rows: 1
  :widths: 1 4
  :class: first-col-right

  + - Value (:term:`uint8 <int>`)
    - Description

  + - :val:`0x00`
    - :enum:`Top`

  + - :val:`0x01`
    - :enum:`Front`

  + - :val:`0x02`
    - :enum:`Right`

  + - :val:`0x03`
    - :enum:`Bottom`

  + - :val:`0x04`
    - :enum:`Back`

  + - :val:`0x05`
    - :enum:`Left`


Program Action
**************

.. list-table::
  :header-rows: 1
  :widths: 1 4
  :class: first-col-right

  + - Value (:term:`uint8 <int>`)
    - Description

  + - :val:`0x00`
    - :enum:`Start`

  + - :val:`0x01`
    - :enum:`Stop`


Response Status
****************

.. list-table::
  :header-rows: 1
  :widths: 1 4
  :class: first-col-right

  + - Value (:term:`uint8 <int>`)
    - Description

  + - :val:`0x00`
    - :enum:`Acknowledged`

  + - :val:`0x01`
    - :enum:`Not Acknowledged`


Motor End State
***************

.. list-table::
  :header-rows: 1
  :widths: 1 4
  :class: first-col-right

  + - Value (:term:`int8 <int>`)
    - Description

  + - :val:`0x00`
    - :enum:`Coast`

  + - :val:`0x01`
    - :enum:`Brake`

  + - :val:`0x02`
    - :enum:`Hold`

  + - :val:`0x03`
    - :enum:`Continue`

  + - :val:`0x04`
    - :index:`\ <Motor End State; Coast (smart)>`
      Coast (:term:`smart <smart coast/brake>`)

  + - :val:`0x05`
    - :index:`\ <Motor End State; Brake (smart)>`
      Brake (:term:`smart <smart coast/brake>`)

  + - :val:`0xFF`
    - :enum:`Default`


Motor Move Direction
********************

.. list-table::
  :header-rows: 1
  :widths: 1 4
  :class: first-col-right

  + - Value (:term:`uint8 <int>`)
    - Description

  + - :val:`0x00`
    - :enum:`Clockwise`

  + - :val:`0x01`
    - :enum:`Counter-Clockwise`

  + - :val:`0x02`
    - :enum:`Shortest Path`

  + - :val:`0x03`
    - :enum:`Longest Path`


Motor Device Type
*****************

.. list-table::
  :header-rows: 1
  :widths: 1 4
  :class: first-col-right

  + - Value (:term:`uint8 <int>`)
    - Description

  + - :val:`0x30`
    - :enum:`Medium Motor`

  + - :val:`0x31`
    - :enum:`Large Motor`

  + - :val:`0x41`
    - :enum:`Small Motor`
