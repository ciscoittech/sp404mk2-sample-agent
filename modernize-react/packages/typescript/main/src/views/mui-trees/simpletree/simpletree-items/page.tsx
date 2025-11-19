

import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import { Grid } from "@mui/material";
import BasicSimpleTreeView from "src/components/muitrees/simpletree/BasicSimpleTreeView";
import TrackitemclicksTree from "src/components/muitrees/simpletree/TrackitemclicksTree";

const BCrumb = [
    {
        to: "/",
        title: "Home",
    },
    {
        title: "SimpleTreeView ",
    },
];

const SimpleTreeView = () => {
    return (
        <PageContainer title="SimpleTreeView" description="this is SimpleTreeView ">
            <Breadcrumb title="SimpleTreeView" items={BCrumb} />
            <Grid container spacing={3}>

                <BasicSimpleTreeView />

                <TrackitemclicksTree />

            </Grid>
        </PageContainer>
    );
};

export default SimpleTreeView;
