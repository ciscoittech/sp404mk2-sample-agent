'use client'
import React from 'react'
import { useTheme } from "@mui/material";
import ParentCard from "../../../shared/ParentCard";
import { ChartContainer } from '@mui/x-charts/ChartContainer';
import {
    LinePlot,
    MarkPlot,
} from '@mui/x-charts/LineChart';
import TinyLineCode from '../../code/linechartscode/TinyLineCode';

function TinyLineChart() {
    const pData = [2400, 1398, 9800, 3908, 4800, 3800, 4300];
    const xLabels = [
        'Page A',
        'Page B',
        'Page C',
        'Page D',
        'Page E',
        'Page F',
        'Page G',
    ];
    const theme = useTheme();
    const primary = theme.palette.primary.main;

    return (
        <ParentCard title="Tiny Chart" codeModel={<TinyLineCode />}>

            <ChartContainer
                width={800}
                height={300}
                series={[{ type: 'line', data: pData, color: primary }]}
                xAxis={[{ scaleType: 'point', data: xLabels }]}
                disableAxisListener
            >
                <LinePlot />
                <MarkPlot />
            </ChartContainer>
        </ParentCard>
    )
}

export default TinyLineChart
