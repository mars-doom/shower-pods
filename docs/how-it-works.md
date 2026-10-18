# How it works

<!--
Start here: in a sentence or two, how does it work? Imagine explaining it to a
curious friend standing next to it. What goes in, what happens, what comes out?
-->
Each pod is built from two IBC totes stacked with a door cut in, a standing platform, and a drain. The hot water "tanks" are individual 6" diameter ABS tubes that are easily detached and placed in a separate solar charging device. The tube is easily carried and filled from a spigot or faucet, charged, and then plugged into the shower pod, which has either a valve or vessel for taking in the hot water.

With individual hot water tanks, everyone can see after their own hot water and it is impossible for one person to (accidentally?) drain a communal hot water tank.

![IBC shower pod concept: exploded view and hot water tube process](images/journal_261018_concept1.jpg)

<!--
Then show what it's made of and how the pieces fit together. Any of these work:

- A sketch on paper with the main parts labeled, photographed with your phone
- A photo of the thing with labels added
- A CAD render or exploded view
- A text diagram that draws itself. Write lines like these:

      flowchart LR
        A[Solar panel] --- B[Heater] --- C[(Tank)]

  and wrap them in a code block whose first line is three backticks
  followed by the word mermaid, and whose last line is three backticks.
  (For arrows instead of lines, use two dashes and a greater-than sign.)

Tip: name the main parts in your diagram the same way you name the sections in
your parts list. Then the picture and the list explain each other.
-->

<!-- Walk through the main parts: what each one does and how it connects to the next. -->

## Goals and constraints

This project is organized into two phases:

**Phase 1: Build Something That Works**
Build 1-2 shower pods that are:

- Low Cost
- Wind Sheltered
- Very Water Efficient (~2.5g/shower)
- Safe (no scalding, no legionella, no bacteria)
- Disposes of greywater appropriately (don't just daylight it somewhere inconvenient)
- Avoids *by design* conflicts that can arise when a group of people have access to a shower with limited water and heat generation.

**Phase 2: Improvements and Stretch Goals**
Once working prototypes are operational, the remainder of the project is to explore improvements:

- Build a Showerloop (recirculating shower water with a pump, sand and charcoal filter, and UV sterilization).
- Build a contained greywater treatment cell.
- Occupied/nonoccupied lights.
- Centralized DHW tank with surplus PV production
- Thermosiphon solar HW heating elements

## References

Sources of ideas and inspiration for this build:

- [48v PV Water Distillation YT](https://www.youtube.com/watch?v=8D7_pEdMu-Q&t=11s)
- [Two-Tote Shower Stall Build Video YT](https://www.youtube.com/watch?v=XP12uxLF4ZU&t=1s)
- [Showerloop Recirculating Shower DIY Instructables](https://www.instructables.com/Showerloop/)
- [Recirculating shower paper (PDF)](https://github.com/mars-doom/shower-pods/blob/main/files/references/recirculatingshower_Paper.pdf)

## Parts

<!--
This list is built automatically from parts.csv. Edit that file (it opens as
a spreadsheet in Pages CMS), not this page.
-->

{{ parts_list }}

## Files

<!--
Everything in the files folder is listed here automatically: CAD models,
drawings, cut files, code, data. Upload files under Media → Files.
-->

{{ files_list }}
