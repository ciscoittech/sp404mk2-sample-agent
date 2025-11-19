
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
        title: "SimpleTreeView ",
    },
];

const SimpleTreeView = () => {
    return (
        <PageContainer title="SimpleTreeView" description="this is SimpleTreeView ">
            <Breadcrumb title="SimpleTreeView" items={BCrumb} />
            <Grid container spacing={3}>
                <ApiMethodFocusItem />

            </Grid>
        </PageContainer>
    );
};

export default SimpleTreeView;
