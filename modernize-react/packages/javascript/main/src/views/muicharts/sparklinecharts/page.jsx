

"use client"
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import { Grid } from "@mui/material";
import BasicSparkLine from "src/components/muicharts/sparklinecharts/BasicSparkLine";
import AreaSparkLineChart from "src/components/muicharts/sparklinecharts/AreaSparkLineChart";
import BasicSparkLineCustomizationChart from "src/components/muicharts/sparklinecharts/BasicSparkLineCustomizationChart";

const BCrumb = [
    {
        to: "/",
        title: "Home",
    },
    {
        title: "SparkLine Charts ",
    },
];

const SparkLineCharts = () => {
    return (
        <PageContainer title="SparkLine Charts" description="this is SparkLine Charts ">

            <Breadcrumb title="SparkLine Charts" items={BCrumb} />
            <Grid container spacing={3}>

                <BasicSparkLine />


                <AreaSparkLineChart />


                <BasicSparkLineCustomizationChart />


            </Grid>
        </PageContainer>
    );
};

export default SparkLineCharts;
