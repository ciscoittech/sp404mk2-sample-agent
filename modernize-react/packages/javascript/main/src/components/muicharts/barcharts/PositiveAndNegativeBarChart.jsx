'use client'
import React from 'react'
import { BarChart } from '@mui/x-charts/BarChart';
import { useTheme } from '@mui/material';
import ParentCard from '../../shared/ParentCard';
import PositiveAndNegativeBarCode from '../code/barchartcode/PositiveAndNegativeBarCode'

function PositiveAndNegativeBarChart() {
    const uData = [4000, 3000, 2000, 2780, 1890, 2390, 3490];
    const pData = [2400, 1398, -9800, 3908, 4800, -3800, 4300];

    const xLabels = [
        "Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Week 7"
    ];

    const theme = useTheme();
    const primary = theme.palette.primary.main;
    const success = theme.palette.success.main;

    return (
        <ParentCard title="Positive And Negative Chart" codeModel={<PositiveAndNegativeBarCode />}>

            <BarChart
                height={300}
                borderRadius={6}
                series={[
                    {
                        data: pData,
                        label: 'Page Views',
                        color: primary
                    },
                    {
                        data: uData,
                        label: ' Visitors',
                        color: success
                    },
                ]}
                xAxis={[
                    {
                        data: xLabels,
                        scaleType: 'band',
                        categoryGapRatio: 0.8,
                        barGapRatio: 0.8
                    },
                ]}
                yAxis={[{
                    max: 10000,


                }]}
            />
        </ParentCard>
    )
}

export default PositiveAndNegativeBarChart
