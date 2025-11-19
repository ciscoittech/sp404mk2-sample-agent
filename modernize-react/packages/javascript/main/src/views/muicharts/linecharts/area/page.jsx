import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import { Grid } from "@mui/material";
import SimpleAreaChart from "src/components/muicharts/linescharts/areacharts/SimpleAreaChart";
import StackedAreaChart from "src/components/muicharts/linescharts/areacharts/StackedAreaChart";
import TinyAreaChart from "src/components/muicharts/linescharts/areacharts/TinyAreaChart";
import PercentAreaChart from "src/components/muicharts/linescharts/areacharts/PercentAreaChart";
import AreaChartConnectNulls from "src/components/muicharts/linescharts/areacharts/AreaChartConnectNullsChart";
import AreaChartFillByValueChart from "src/components/muicharts/linescharts/areacharts/AreaChartFillByValueChart";
const BCrumb = [
    {
        to: "/",
        title: "Home",
    },
    {
        title: " Area Charts",
    },
];

const AreaCharts = () => {
    return (
        <PageContainer title=" Area Charts" description="this is  Area Chart">
            <Breadcrumb title=" Area  Charts" items={BCrumb} />
            <Grid container spacing={3}>

                <SimpleAreaChart />


                <StackedAreaChart />


                <TinyAreaChart />


                <PercentAreaChart />


                <AreaChartConnectNulls />


                <AreaChartFillByValueChart />



            </Grid>
        </PageContainer>
    );
};

export default AreaCharts;
