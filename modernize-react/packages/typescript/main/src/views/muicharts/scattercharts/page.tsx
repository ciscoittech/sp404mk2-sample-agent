"use client"
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import { Grid } from "@mui/material";
import BasicScatterChart from "src/components/muicharts/scattercharts/BasicScatterChart";
import ScatterDatasetChart from "src/components/muicharts/scattercharts/ScatterDatasetChart";
import VoronoiInteractionChart from "src/components/muicharts/scattercharts/VoronoiInteractionChart";
import ScatterClickNoSnapChart from "src/components/muicharts/scattercharts/ScatterClickNoSnapChart";

const BCrumb = [
    {
        to: "/",
        title: "Home",
    },
    {
        title: "ScatterCharts ",
    },
];

const ScatterCharts = () => {
    return (
        <PageContainer title="ScatterCharts" description="this is ScatterCharts ">

            <Breadcrumb title="ScatterCharts" items={BCrumb} />
            <Grid container spacing={3}>

                <BasicScatterChart />

                <ScatterDatasetChart />

                <VoronoiInteractionChart />

                <ScatterClickNoSnapChart />


            </Grid>
        </PageContainer>
    );
};

export default ScatterCharts;
