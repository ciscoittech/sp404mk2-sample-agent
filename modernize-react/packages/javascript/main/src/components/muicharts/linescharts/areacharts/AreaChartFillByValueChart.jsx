'use client'
import * as React from 'react';
import { green, red } from '@mui/material/colors';
import Stack from '@mui/material/Stack';
import { useYScale, useDrawingArea } from '@mui/x-charts/hooks';
import { LineChart, areaElementClasses } from '@mui/x-charts/LineChart';
import { useTheme } from '@mui/material';
import ParentCard from "src/components/shared/ParentCard";
import AreaChartFillByValueCode from '../../code/areachartscode/AreaChartFillByValueCode';




function ColorSwich({ threshold, color1, color2, id }) {

    const { top, height, bottom } = useDrawingArea();
    const svgHeight = top + bottom + height;

    const scale = useYScale(); // You can provide the axis Id if you have multiple ones
    const y0 = scale(threshold); // The coordinate of of the origine
    const off = y0 !== undefined ? y0 / svgHeight : 0;

    return (
        <defs>
            <linearGradient
                id={id}
                x1="0"
                x2="0"
                y1="0"
                y2={`${svgHeight}px`}
                gradientUnits="userSpaceOnUse" // Use the SVG coordinate instead of the component ones.
            >
                <stop offset={off} stopColor={color1} stopOpacity={1} />
                <stop offset={off} stopColor={color2} stopOpacity={1} />
            </linearGradient>
        </defs>
    );
}

export default function AreaChartFillByValue() {
    const data = [4000, 3000, -1000, 500, -2100, -250, 3490];
    const xData = ["January", "February", "March", "April", "May", "June", "July"];

    const theme = useTheme();
    const primary = theme.palette.primary.main;
    const amtDatacolor = theme.palette.error.main;

    return (
        <ParentCard title=" FillByValue Chart" codeModel={<AreaChartFillByValueCode />}>

            <Stack direction="column" width="100%" spacing={1}>
                <LineChart
                    xAxis={[{ data: xData, scaleType: 'point' }]}
                    yAxis={[{ min: -3000, max: 4000 }]}
                    series={[{ data, showMark: false, area: true }]}
                    height={200}
                    margin={{ top: 20, bottom: 30, left: 75 }}
                    sx={{
                        [`& .${areaElementClasses.root}`]: {
                            fill: 'url(#swich-color-id-1)',
                        },
                    }}
                >
                    <ColorSwich
                        color1={primary}
                        color2={amtDatacolor}
                        threshold={0}
                        id="swich-color-id-1"
                    />
                    <rect x={0} y={0} width={5} height="100%" fill="url(#swich-color-id-1)" />
                </LineChart>

                <LineChart
                    xAxis={[{ data: xData, scaleType: 'point' }]}
                    yAxis={[{ min: -3000, max: 4000 }]}
                    series={[{ data, showMark: false, area: true }]}
                    height={200}
                    margin={{ top: 20, bottom: 30, left: 75 }}
                    sx={{
                        [`& .${areaElementClasses.root}`]: {
                            fill: 'url(#swich-color-id-2)',
                        },
                    }}
                >
                    <ColorPalette id="swich-color-id-2" />

                    <rect x={0} y={0} width={5} height="100%" fill="url(#swich-color-id-2)" />
                </LineChart>
            </Stack>
        </ParentCard>
    );
}

function ColorPalette({ id }) {
    const { top, height, bottom } = useDrawingArea();
    const svgHeight = top + bottom + height;

    const scale = useYScale();

    return (
        <defs>
            <linearGradient
                id={id}
                x1="0"
                x2="0"
                y1="0"
                y2={`${svgHeight}px`}
                gradientUnits="userSpaceOnUse" // Use the SVG coordinate instead of the component ones.
            >
                <stop
                    offset={scale(5000) / svgHeight}
                    stopColor={green[400]}
                    stopOpacity={1}
                />
                <stop
                    offset={scale(4000) / svgHeight}
                    stopColor={green[400]}
                    stopOpacity={1}
                />
                <stop
                    offset={scale(4000) / svgHeight}
                    stopColor={green[300]}
                    stopOpacity={1}
                />
                <stop
                    offset={scale(3000) / svgHeight}
                    stopColor={green[300]}
                    stopOpacity={1}
                />
                <stop
                    offset={scale(3000) / svgHeight}
                    stopColor={green[200]}
                    stopOpacity={1}
                />
                <stop
                    offset={scale(2000) / svgHeight}
                    stopColor={green[200]}
                    stopOpacity={1}
                />
                <stop
                    offset={scale(2000) / svgHeight}
                    stopColor={green[100]}
                    stopOpacity={1}
                />
                <stop
                    offset={scale(1000) / svgHeight}
                    stopColor={green[100]}
                    stopOpacity={1}
                />
                <stop
                    offset={scale(1000) / svgHeight}
                    stopColor={green[50]}
                    stopOpacity={1}
                />
                <stop offset={scale(0) / svgHeight} stopColor={green[50]} stopOpacity={1} />
                <stop offset={scale(0) / svgHeight} stopColor={red[100]} stopOpacity={1} />
                <stop
                    offset={scale(-1000) / svgHeight}
                    stopColor={red[100]}
                    stopOpacity={1}
                />
                <stop
                    offset={scale(-1000) / svgHeight}
                    stopColor={red[200]}
                    stopOpacity={1}
                />
                <stop
                    offset={scale(-2000) / svgHeight}
                    stopColor={red[200]}
                    stopOpacity={1}
                />
                <stop
                    offset={scale(-3000) / svgHeight}
                    stopColor={red[300]}
                    stopOpacity={1}
                />
            </linearGradient>
        </defs>
    );
}
