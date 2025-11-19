"use client";

import { LineChart } from "@mui/x-charts/LineChart";
import BiaxialLineCode from "../../code/linechartscode/BiaxialLineCode";
import ParentCard from 'src/components/shared/ParentCard';
import { useTheme } from "@mui/material";

export default function BiaxialLineChart() {

    const monthlyProfits = [4000, 3000, 2000, 2780, 1890, 2390, 3490];
    const monthlyRevenue = [2400, 1398, 9800, 3908, 4800, 3800, 4300];
    const xLabels = ["January", "February", "March", "April", "May", "June", "July"];

    const theme = useTheme();
    const primary = theme.palette.primary.main;
    const secondary = theme.palette.secondary.main;
    return (
        <ParentCard title="Biaxial Chart" codeModel={<BiaxialLineCode />}>
            <LineChart
                height={300}
                series={[
                    { data: monthlyRevenue, label: "Revenue", yAxisId: "leftAxisId", color: primary },
                    {
                        data: monthlyProfits,
                        label: "Profits",
                        yAxisId: "rightAxisId",
                        color: secondary,
                    },
                ]}
                xAxis={[{ scaleType: "point", data: xLabels }]}
                yAxis={[{ id: "leftAxisId" }, { id: "rightAxisId", position: 'right' }]}

            />
        </ParentCard>
    );
}
