'use client'
import * as React from 'react';
import { BarChart } from '@mui/x-charts/BarChart';
import ParentCard from '../../shared/ParentCard';
import SimpleBarCode from '../code/barchartcode/SimpleBarCode'
import { useTheme } from '@mui/material';


export default function SimpleBarChart() {

    const uData = [4000, 3000, 2000, 2780, 1890, 2390, 3490];
    const pData = [2400, 1398, 9800, 3908, 4800, 3800, 4300];

    const xLabels = [
        "Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Week 7"
    ];


    const theme = useTheme();
    const primary = theme.palette.primary.main;
    const secondary = theme.palette.secondary.main;

    return (
        <ParentCard title="Simple Chart" codeModel={<SimpleBarCode />}>
            <BarChart
                height={300}
                borderRadius={6}
                series={[
                    { data: pData, label: 'Page Views', id: 'pId', color: primary },
                    { data: uData, label: ' Visitors', id: 'uId', color: secondary },

                ]}
                xAxis={[{
                    data: xLabels, scaleType: 'band',
                    categoryGapRatio: 0.8,
                    barGapRatio: 0.8
                }]}
            />
        </ParentCard>
    );
}