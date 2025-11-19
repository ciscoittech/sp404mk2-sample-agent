
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';

import TinyBarChart from 'src/components/muicharts/barcharts/SimpleBarChart'
import StackedBarChart from 'src/components/muicharts/barcharts/StackedBarChart'
import SimpleBarChart from "src/components/muicharts/barcharts/SimpleBarChart";
import MixedBarChart from 'src/components/muicharts/barcharts/MixedBarChart'
import PositiveAndNegativeBarChart from "src/components/muicharts/barcharts/PositiveAndNegativeBarChart";
import BarChartStackedBySignChart from "src/components/muicharts/barcharts/BarChartStackedBySignChart";
import { Grid } from "@mui/material";
import BiaxialBarChart from "src/components/muicharts/barcharts/BiaxialBarChart";

const BCrumb = [
    {
        to: "/",
        title: "Home",
    },
    {
        title: "Bar Charts",
    },
];

const BarChart = () => {
    return (
        <PageContainer title="Bar Chart" description="this is Bar Chart">
            <Breadcrumb title="Bar Chart" items={BCrumb} />
            <Grid container spacing={3}>
                <Grid
                    size={{
                        md: 6
                    }}
                >
                    <SimpleBarChart />
                </Grid>

                <Grid size={{
                    md: 6
                }} >
                    <MixedBarChart />
                </Grid>
                <Grid size={{

                    md: 6
                }}>
                    <PositiveAndNegativeBarChart />
                </Grid>
                <Grid size={{

                    md: 6
                }} >
                    <BarChartStackedBySignChart />
                </Grid>
                <Grid size={{
                    md: 6
                }}>
                    <BiaxialBarChart />
                </Grid>
                <Grid
                    size={{
                        md: 6
                    }}>
                    <StackedBarChart />

                </Grid>
                <Grid size={{
                    md: 6
                }}>
                    <TinyBarChart />
                </Grid>
            </Grid>
        </PageContainer>
    );
};

export default BarChart;
