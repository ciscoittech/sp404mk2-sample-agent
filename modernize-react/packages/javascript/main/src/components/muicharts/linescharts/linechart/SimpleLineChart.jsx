'use client'
import React from 'react'
import { LineChart } from '@mui/x-charts/LineChart';
import { useTheme } from "@mui/material";
import ParentCard from "../../../shared/ParentCard";
import SimpleLineCode from '../../code/linechartscode/SimpleLineCode';

function SimpleLineChart() {




    const monthlyProfits = [4000, 3000, 2000, 2780, 1890, 2390, 3490];
    const monthlyRevenue = [2400, 1398, 9800, 3908, 4800, 3800, 4300];

    const xLabels = ["January", "February", "March", "April", "May", "June", "July"];


    const theme = useTheme();
    const primary = theme.palette.primary.main;
    const secondary = theme.palette.secondary.main;
    return (
        <ParentCard title="Simple Chart" codeModel={<SimpleLineCode />}>

            <LineChart
                height={300}
                series={[
                    { data: monthlyRevenue, label: 'Revenue', color: primary },
                    { data: monthlyProfits, label: 'Profits', color: secondary },
                ]}
                xAxis={[{ scaleType: 'point', data: xLabels }]}
            />
        </ParentCard>
    )
}

export default SimpleLineChart
