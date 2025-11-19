import PageContainer from 'src/components/container/PageContainer';
import HeaderAlert from '../../../components/frontend-pages/shared/header/HeaderAlert';
import HpHeader from '../../../components/frontend-pages/shared/header/HpHeader';
import Pricing from '../../../components/frontend-pages/shared/pricing';
import C2a from '../../../components/frontend-pages/shared/c2a';
import Footer from '../../../components/frontend-pages/shared/footer';
import Banner from '../../../components/frontend-pages/pricing/Banner';
import ScrollToTop from '../../../components/frontend-pages/shared/scroll-to-top';

const PricingPage = () => {
    return (
        <PageContainer title="Pricing" description="this is Pricing">

            <HeaderAlert />
            <HpHeader />
            <Banner />
            <Pricing />
            <C2a />
            <Footer />
            <ScrollToTop />
        </PageContainer>
    );
};

export default PricingPage;
