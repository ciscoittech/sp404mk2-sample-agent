
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import { Grid } from "@mui/material";
import MultiSelectTreeView from "src/components/muitrees/simpletree/MultiSelectTreeView";
import CheckboxSelection from "src/components/muitrees/simpletree/CheckboxSelection";
import ControlledSelectiontree from "src/components/muitrees/simpletree/ControlledSelectiontree";

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

                <MultiSelectTreeView />


                <CheckboxSelection />


                <ControlledSelectiontree />


            </Grid>
        </PageContainer>
    );
};

export default SimpleTreeView;
