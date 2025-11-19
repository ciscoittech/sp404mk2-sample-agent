import CodeDialog from '../../../shared/CodeDialog';

const ControlledCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import {
  Accordion,
  AccordionSummary,
  Typography,
  AccordionDetails,
} from "@mui/material";
import { IconChevronDown } from '@tabler/icons';

<Accordion
    expanded={expanded === "panel1"}
    onChange={handleChange("panel1")}
    >
    <AccordionSummary
        expandIcon={<IconChevronDown />}
        aria-controls="panel1bh-content"
        id="panel1bh-header"
    >
        <Typography variant="h6" sx={{ width: "33%", flexShrink: 0 }}>
        General settings
        </Typography>
        <Typography variant="subtitle2" color="textSecondary">
        I am an accordion
        </Typography>
    </AccordionSummary>
    <AccordionDetails>
        <Typography variant="subtitle1" color="textSecondary">
        Nulla facilisi. Phasellus sollicitudin nulla et quam mattis
        feugiat. Aliquam eget maximus est, id dignissim quam.
        </Typography>
    </AccordionDetails>
    </Accordion>
    <Accordion
    expanded={expanded === "panel2"}
    onChange={handleChange("panel2")}
    >
    <AccordionSummary
        expandIcon={<IconChevronDown />}
        aria-controls="panel2bh-content"
        id="panel2bh-header"
    >
        <Typography variant="h6" sx={{ width: "33%", flexShrink: 0 }}>
        Users
        </Typography>
        <Typography variant="subtitle2" color="textSecondary">
        You are currently not an owner
        </Typography>
    </AccordionSummary>
    <AccordionDetails>
        <Typography variant="subtitle1" color="textSecondary">
        Donec placerat, lectus sed mattis semper, neque lectus
        feugiat lectus, varius pulvinar diam eros in elit.
        Pellentesque convallis laoreet laoreet.
        </Typography>
    </AccordionDetails>
    </Accordion>
    <Accordion
    expanded={expanded === "panel3"}
    onChange={handleChange("panel3")}
    >
    <AccordionSummary
        expandIcon={<IconChevronDown />}
        aria-controls="panel3bh-content"
        id="panel3bh-header"
    >
        <Typography variant="h6" sx={{ width: "33%", flexShrink: 0 }}>
        Advanced settings
        </Typography>
        <Typography variant="subtitle2" color="textSecondary">
        Filtering has been entirely disabled for whole web server
        </Typography>
    </AccordionSummary>
    <AccordionDetails>
        <Typography variant="subtitle1" color="textSecondary">
        Nunc vitae orci ultricies, auctor nunc in, volutpat nisl.
        Integer sit amet egestas eros, vitae egestas augue. Duis vel
        est augue.
        </Typography>
    </AccordionDetails>
    </Accordion>
    <Accordion
    expanded={expanded === "panel4"}
    onChange={handleChange("panel4")}
    >
    <AccordionSummary
        expandIcon={<IconChevronDown />}
        aria-controls="panel4bh-content"
        id="panel4bh-header"
    >
        <Typography variant="h6" sx={{ width: "33%", flexShrink: 0 }}>
        Personal data
        </Typography>
    </AccordionSummary>
    <AccordionDetails>
        <Typography variant="subtitle1" color="textSecondary">
        Nunc vitae orci ultricies, auctor nunc in, volutpat nisl.
        Integer sit amet egestas eros, vitae egestas augue. Duis vel
        est augue.
        </Typography>
    </AccordionDetails>
    </Accordion>`}
      </CodeDialog>
    </>
  );
};

export default ControlledCode;
