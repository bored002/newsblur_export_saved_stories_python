import datetime
class GeneratePage(object):


  @staticmethod
  def update_readme():
    with open('README.md', 'w') as f:
        f.write(f"""# My Project
          ## Current Performance
          
          ![Gauge](/gauge.png)
          
          Last updated: {datetime.now()}
          """)
          
# if __name__ == "__main__":
#   pass
  # update_readme()
