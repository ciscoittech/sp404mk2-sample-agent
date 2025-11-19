
'use client'
import * as React from 'react';
import { PieChart, pieArcLabelClasses } from '@mui/x-charts/PieChart';
import PieChartWithCustomizedLabelCode from '../code/piechartcode/PieChartWithCustomizedLabelCode'
import ParentCard from '../../shared/ParentCard';

const data = [
    { label: 'Group A', value: 400, color: '#5D87FF' },
    { label: 'Group B', value: 300, color: '#0074BA' },
    { label: 'Group C', value: 300, color: '#01C0C8' },
    { label: 'Group D', value: 200, color: '#CCDA4E' },
];

const sizing = {
    margin: { right: 5 },
    width: 200,
    height: 200,
    legend: { hidden: true },
};
const TOTAL = data.map((item) => item.value).reduce((a, b) => a + b, 0);

const getArcLabel = (params) => {
    const percent = params.value / TOTAL;
    return `${(percent * 100).toFixed(0)}%`;
};

export default function PieChartWithCustomizedLabel() {
    return (
        <ParentCard title="CustomizedLabel Chart" codeModel={<PieChartWithCustomizedLabelCode />}>
            <PieChart
                series={[
                    {
                        outerRadius: 80,
                        data,
                        arcLabel: getArcLabel,
                    },
                ]}
                sx={{
                    [`& .${pieArcLabelClasses.root}`]: {
                        fill: 'white',
                        fontSize: 14,
                    },
                }}
                {...sizing}
            />
        </ParentCard>
    );
}