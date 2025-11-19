'use client'
import * as React from 'react';
import Stack from '@mui/material/Stack';
import { LineChart } from '@mui/x-charts/LineChart';
import ParentCard from "src/components/shared/ParentCard";
import { useTheme } from '@mui/material';
import AreaChartConnectNullsCode from '../../code/areachartscode/AreaChartConnectNullsCode';



export default function AreaChartConnectNulls() {
    const data = [4000, 3000, 2000, null, 1890, 2390, 3490];
    const xData = ["January", "February", "March", "April", "May", "June", "July"];
    const theme = useTheme();
    const primary = theme.palette.primary.main;

    return (
        <ParentCard title="ConnectNulls Chart" codeModel={<AreaChartConnectNullsCode />}>

            <Stack sx={{ width: '100%' }}>
                <LineChart
                    xAxis={[{ data: xData, scaleType: 'point' }]}
                    series={[{ data, showMark: false, area: true, color: primary }]}
                    height={200}
                    margin={{ top: 10, bottom: 20 }}
                />
                <LineChart
                    xAxis={[{ data: xData, scaleType: 'point' }]}
                    series={[{ data, showMark: false, area: true, connectNulls: true, color: primary }]}
                    height={200}
                    margin={{ top: 10, bottom: 20 }}
                />
            </Stack>
        </ParentCard>
    );
}