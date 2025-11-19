

import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';


import { Grid } from "@mui/material";
import ControlledExpansionTree from "src/components/muitrees/simpletree/ControlledExpansionTree";
import ApiMethodSetItemExpansion from "src/components/muitrees/simpletree/ApiMethodSetItemExpansion";
const BCrumb = [
    {
        to: "/",
        title: "Home",
    },
    {
        title: "Simple Treeview ",
    },
];

const SimpleTreeView = () => {
    return (
        <PageContainer title="Simple Treeview" description="this is Simple Treeview ">
            <Breadcrumb title="Simple Treeview" items={BCrumb} />
            <Grid container spacing={3}>

                <ControlledExpansionTree />


                <ApiMethodSetItemExpansion />

            </Grid>
        </PageContainer>
    );
};

export default SimpleTreeView;
