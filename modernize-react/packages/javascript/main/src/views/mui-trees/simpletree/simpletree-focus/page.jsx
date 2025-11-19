


import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';


import { Grid } from "@mui/material";
import ApiMethodFocusItem from "src/components/muitrees/simpletree/ApiMethodFocusItem";

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

                <ApiMethodFocusItem />


            </Grid>
        </PageContainer>
    );
};

export default SimpleTreeView;
