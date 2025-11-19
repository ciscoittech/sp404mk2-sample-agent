
"use client"

import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';

import { Grid } from "@mui/material";
import BasicGaugesChart from "src/components/muicharts/gaugecharts/BasicGaugesChart";
import ArcDesignChart from "src/components/muicharts/gaugecharts/ArcDesignChart";
import GaugePointerChart from "src/components/muicharts/gaugecharts/GaugePointerChart";


const BCrumb = [
    {
        to: "/",
        title: "Home",
    },
    {
        title: "Gauge Charts ",
    },
];

const GaugeCharts = () => {
    return (
        <PageContainer title="Gauge Charts" description="this is Gauge Charts ">

            <Breadcrumb title="Gauge Charts" items={BCrumb} />
            <Grid container spacing={3}>
                <Grid
                    size={{
                        md: 6
                    }}
                >
                    <BasicGaugesChart />
                </Grid>
                <Grid
                    size={{
                        md: 6
                    }}
                >

                    <ArcDesignChart />
                </Grid>
                <Grid
                    size={{
                        md: 6
                    }}
                >

                    <GaugePointerChart />
                </Grid>


            </Grid>
        </PageContainer>
    );
};

export default GaugeCharts;
