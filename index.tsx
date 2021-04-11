import React, {
  ReactNode,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import styled from 'styled-components';
import LifeCycle from './_fragments/LifeCycle';
import MobxRender from './_fragments/MobxRender';
import Push from './_fragments/Push';

console.log('ManualContainer download');

const ManualContainer = () => {
  const [fold, setFold] = useState(true);
  const [headerTop, setTop] = useState(0);
  const [scrollY, setScrollY] = useState(0);
  const scrollRef = useRef<any>();
  const focusTarget = useRef<any>([]);

  const scrollToRef = (value: string) => {
    const obj: any = {
      Push: 0,
      LifeCycle: 1,
      MobxRender: 2,
    };
    focusTarget.current[obj[value]].scrollIntoView({
      block: 'center',
      behavior: 'smooth',
    });
  };

  useEffect(() => {
    const handleScroll = () => {
      const scrollNow = scrollRef.current.scrollTop;
      setTop(headerTop - (scrollNow - scrollY));
      if (headerTop - (scrollNow - scrollY) < -80) {
        setTop(-80);
      } else if (headerTop - (scrollNow - scrollY) > 0) {
        setTop(0);
      } else {
        setTop(headerTop - (scrollNow - scrollY));
      }
      setScrollY(scrollNow);
    };
    const handleClick = (e: any) => {
      if (scrollRef.current.scrollTop >= 80) {
        setTop(-80);
      }
      if (e.target.nodeName !== 'LI') {
        if (!fold) {
          setFold(true);
        }
      }
    };
    window.addEventListener('click', handleClick);
    scrollRef.current?.addEventListener('scroll', handleScroll);
    return () => {
      scrollRef.current?.removeEventListener('scroll', handleScroll);
      window.removeEventListener('click', handleClick);
    };
  }, [scrollY, headerTop, fold]);

  return (
    <Container ref={scrollRef}>
      {/* {console.log('ManualContainer render')} */}
      <Header top={headerTop} className={fold ? 'fold' : 'unfold'}>
        <Title
          className="header"
          onClick={() => {
            const elements = document.getElementsByClassName('header');
            for (var i = 0; i < elements.length; i++) {
              elements[i].classList.remove('bounce');
            }
            void elements[0].clientWidth;
            for (var i = 0; i < elements.length; i++) {
              elements[i].classList.add('bounce');
            }
          }}
        >
          Manual
        </Title>
        <ContentBox>
          <ContentIndex
            className={`header ${fold ? 'fold' : 'unfold'}`}
            onClick={() => setFold(!fold)}
          >
            Contents
          </ContentIndex>
          <Contents className={fold ? 'fold' : 'unfold'}>
            <ContentItem onClick={() => scrollToRef('Push')}>Push</ContentItem>
            <ContentItem onClick={() => scrollToRef('LifeCycle')}>
              Life Cycle
            </ContentItem>
            <ContentItem onClick={() => scrollToRef('MobxRender')}>
              Mobx Render
            </ContentItem>
          </Contents>
        </ContentBox>
      </Header>
      <ManualBox>
        <ManualItem>
          <Push
            handleRef={(element: any) => (focusTarget.current[0] = element)}
          />
        </ManualItem>
        <ManualItem>
          <LifeCycle
            handleRef={(element: any) => (focusTarget.current[1] = element)}
          />
        </ManualItem>
        <ManualItem>
          <MobxRender
            handleRef={(element: any) => (focusTarget.current[2] = element)}
          />
        </ManualItem>
      </ManualBox>
    </Container>
  );
};

export default ManualContainer;

const Container = styled.div<any>`
  height: 100vh;
  position: relative;
  overflow-y: scroll;
  animation-name: start;
  animation-duration: 0.2s;
  @keyframes start {
    0% {
      opacity: 1;
      left: 1000px;
    }
    100% {
      opacity: 1;
      left: 0px;
    }
  }
`;

const Header = styled.div<any>`
  height: 80px;
  background-color: #0a043c;
  width: 100%;
  top: ${(props) => props.top}px;
  position: fixed;
  z-index: 10;
  display: flex;
  justify-content: space-around;
  align-items: center;

  &.unfold {
    top: 0px;
  }
`;

const Title = styled.h1`
  color: #c7cfb7;
  position: relative;
  font-size: 2rem;
  :hover {
    cursor: pointer;
  }
  &.bounce {
    animation-name: bounce;
    animation-duration: 1s;
    @keyframes bounce {
      0%,
      20%,
      50%,
      80%,
      100% {
        -webkit-transform: translateY(0);
      }
      40% {
        -webkit-transform: translateY(-30px);
      }
      60% {
        -webkit-transform: translateY(-20px);
      }
    }
  }
`;

const ContentBox = styled.div`
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
`;

const ContentIndex = styled.button`
  position: relative;
  color: #c7cfb7;
  font-size: 2rem;
  border: 0;
  background-color: #0a043c;
  :hover {
    font-weight: bold;
  }
  &.unfold {
    font-weight: bold;
  }
  &.bounce {
    animation-name: bounce;
    animation-duration: 1s;
  }
`;

const Contents = styled.ul`
  padding: 0 10px 10px 10px;
  position: absolute;
  text-align: center;
  background-color: #0a043c;
  border-radius: 0 0 10px 10px;
  width: 100%;
  top: 100%;
  color: #c7cfb7;
  font-size: 1.2rem;
  display: none;

  &.unfold {
    display: block;
    animation-name: drop;
    animation-duration: 2s;
    @keyframes drop {
      0% {
        opacity: 0;
      }
      100% {
        opacity: 1;
      }
    }
  }
`;

const ContentItem = styled.li`
  margin-bottom: 10px;
  :hover {
    cursor: pointer;
  }
`;

const ManualBox = styled.div`
  margin-top: 80px;
`;

const ManualItem = styled.div`
  background-color: #f7f7e8;
  padding: 20px;
  margin-bottom: 20px;
`;
