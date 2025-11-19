'use client'
import * as React from 'react';
import Stack from '@mui/material/Stack';
import { Gauge } from '@mui/x-charts/Gauge';
import ParentCard from "src/components/shared/ParentCard";
import BasicGaugesCode from '../code/gaugechartscode/BasicGaugesCode';

export default function BasicGaugesChart() {
    return (
        <ParentCard title="Basic Chart" codeModel={<BasicGaugesCode />}>

            <Stack direction={{ xs: 'column', md: 'row' }} spacing={{ xs: 1, md: 3 }}>
                <Gauge width={200} height={200} value={60} />
                <Gauge width={200} height={200} value={60} startAngle={-90} endAngle={90} />
            </Stack>
        </ParentCard>
    );
}
